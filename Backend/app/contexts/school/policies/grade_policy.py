from typing import Any, Dict, Optional

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import by_show_deleted, not_deleted, ShowDeleted
from app.contexts.shared.lifecycle.policy_result import PolicyResult


class GradePolicy:
    """
    Policy aligned with CURRENT schema (no new fields):

      grades: { student_id, class_id, subject_id, teacher_id, type, term, score, lifecycle... }
      teacher_subject_assignments: { teacher_id, class_id, subject_id, lifecycle... }
      classes: { homeroom_teacher_id, status, lifecycle... }
      subjects: { is_active, lifecycle... }
      students: { current_class_id, lifecycle... }

    Target behavior (practical for production):
      - Create grade:
          * Assigned subject-teacher can create grades in that class/subject.
          * Optional: homeroom can override (if you want).
          * Multiple grades allowed (homework/quiz can be created many times).
      - Update/Delete grade:
          * Homeroom can manage all grades in their class (optional).
          * Assigned subject-teacher can manage grades for that subject in that class (co-teacher).
          * Optional: creator can always edit their own grade (fallback).
      - List class grades:
          * Homeroom can view all grades in class (optionally filtered by subject).
          * Non-homeroom:
              - must provide subject_id
              - must be assigned to that subject in that class
              - can only see THEIR OWN grades (enforced in build_list_filter)
    """

    def __init__(self, db: Database):
        self.db = db
        self.subjects = db["subjects"]
        self.classes = db["classes"]
        self.students = db["students"]
        self.grades = db["grades"]
        self.assignments = db["teacher_subject_assignments"]

    # -------------------------
    # Helpers
    # -------------------------

    def _get_class_for_guard(self, *, class_id: ObjectId) -> dict | None:
        return self.classes.find_one(
            not_deleted({"_id": class_id}),
            {"_id": 1, "homeroom_teacher_id": 1, "status": 1},
        )

    def _is_homeroom(self, *, teacher_id: ObjectId, class_id: ObjectId) -> bool:
        cls = self._get_class_for_guard(class_id=class_id)
        if not cls:
            return False
        return cls.get("homeroom_teacher_id") == teacher_id

    def _teacher_assigned(self, *, teacher_id: ObjectId, class_id: ObjectId, subject_id: ObjectId) -> bool:
        q = not_deleted(
            {
                "teacher_id": teacher_id,
                "class_id": class_id,
                "subject_id": subject_id,
            }
        )
        return self.assignments.count_documents(q, limit=1) > 0

    def _get_grade_for_guard(self, *, grade_id: ObjectId) -> dict | None:
        return self.grades.find_one(
            not_deleted({"_id": grade_id}),
            {"_id": 1, "class_id": 1, "subject_id": 1, "teacher_id": 1},
        )

    # -------------------------
    # CREATE
    # -------------------------

    def can_create(
        self,
        *,
        student_id: ObjectId,
        subject_id: ObjectId,
        teacher_id: ObjectId,
        class_id: ObjectId,
        term: str | None = None,
        grade_type: str | None = None,
        require_student_in_class: bool = False,
        # IMPORTANT: default False to allow multiple grades (homework, quizzes, etc.)
        prevent_duplicate: bool = False,
        # Optional: allow homeroom to create grades even if not assigned to subject
        allow_homeroom_override: bool = False,
    ) -> PolicyResult:
        # Subject must exist + not deleted + active
        subj = self.subjects.find_one(
            not_deleted({"_id": subject_id}),
            {"_id": 1, "is_active": 1},
        )
        if not subj:
            return PolicyResult.deny("create", {"subject": "not_found_or_deleted"})
        if subj.get("is_active") is False:
            return PolicyResult.deny("create", {"subject": "inactive"})

        # Class must exist + not deleted + allowed status
        class_doc = self._get_class_for_guard(class_id=class_id)
        if not class_doc:
            return PolicyResult.deny("create", {"class": "not_found_or_deleted"})

        status = class_doc.get("status")
        if status in ("inactive", "archived"):
            return PolicyResult.deny("create", {"class_status": status})

        # Authorization:
        # Default: assigned subject-teacher only.
        # Optional: homeroom override if you enable it.
        is_homeroom = (class_doc.get("homeroom_teacher_id") == teacher_id)
        if not (allow_homeroom_override and is_homeroom):
            if not self._teacher_assigned(teacher_id=teacher_id, class_id=class_id, subject_id=subject_id):
                return PolicyResult.deny("create", {"permission": "not_assigned_for_subject"})

        # Optional: student must be currently in this class
        if require_student_in_class:
            stu = self.students.find_one(
                not_deleted({"_id": student_id}),
                {"_id": 1, "current_class_id": 1},
            )
            if not stu:
                return PolicyResult.deny("create", {"student": "not_found_or_deleted"})

            if stu.get("current_class_id") != class_id:
                return PolicyResult.deny(
                    "create",
                    {
                        "enrollment": "student_not_in_class",
                        "student_current_class_id": str(stu.get("current_class_id")) if stu.get("current_class_id") else None,
                    },
                )

        # Duplicate prevention (NOT recommended with current schema)
        # With your schema, preventing duplicates usually blocks legitimate "homework #1, #2, #3".
        # Keep OFF unless you intentionally want 1 grade per (student, subject, term, type[, class]).
        if prevent_duplicate:
            q: Dict[str, Any] = not_deleted(
                {
                    "student_id": student_id,
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "term": term,
                }
            )
            if grade_type is not None:
                q["type"] = grade_type

            existing = self.grades.find_one(q, {"_id": 1})
            if existing:
                return PolicyResult.deny(
                    "create",
                    {"duplicate": "grade_already_exists", "existing_grade_id": str(existing["_id"])},
                )

        return PolicyResult.ok("create")

    # -------------------------
    # UPDATE / DELETE
    # -------------------------

    def can_modify(
        self,
        *,
        grade_id: ObjectId,
        teacher_id: ObjectId,
        allow_homeroom_manage_all: bool = True,
        allow_assigned_subject_teacher: bool = True,   # co-teacher can edit grades in their subject
        allow_owner_fallback: bool = True,             # creator can always edit their own grade
    ) -> PolicyResult:
        grade = self._get_grade_for_guard(grade_id=grade_id)
        if not grade:
            return PolicyResult.deny("modify", {"grade": "not_found_or_deleted"})

        class_id: ObjectId | None = grade.get("class_id")
        subject_id: ObjectId | None = grade.get("subject_id")
        owner_id: ObjectId | None = grade.get("teacher_id")

        # 1) Homeroom can manage all grades in the class
        if allow_homeroom_manage_all and class_id:
            if self._is_homeroom(teacher_id=teacher_id, class_id=class_id):
                return PolicyResult.ok("modify")

        # 2) Assigned subject-teacher can manage grades for that class+subject (co-teacher)
        if allow_assigned_subject_teacher and class_id and subject_id:
            if self._teacher_assigned(teacher_id=teacher_id, class_id=class_id, subject_id=subject_id):
                return PolicyResult.ok("modify")

        # 3) Creator can still edit their own grades
        if allow_owner_fallback and owner_id and owner_id == teacher_id:
            return PolicyResult.ok("modify")

        return PolicyResult.deny("modify", {"permission": "forbidden"})

    def can_update(self, grade_id: ObjectId, teacher_id: ObjectId) -> PolicyResult:
        return self.can_modify(grade_id=grade_id, teacher_id=teacher_id)

    def can_soft_delete(self, grade_id: ObjectId, teacher_id: ObjectId) -> PolicyResult:
        return self.can_modify(grade_id=grade_id, teacher_id=teacher_id)

    def can_hard_delete(self, grade_id: ObjectId, teacher_id: ObjectId) -> PolicyResult:
        exists = self.grades.count_documents(by_show_deleted("all", {"_id": grade_id}), limit=1)
        if exists == 0:
            return PolicyResult.deny("hard", {"grade": "not_found"})

        grade = self.grades.find_one(
            by_show_deleted("all", {"_id": grade_id}),
            {"_id": 1, "class_id": 1, "teacher_id": 1},
        )
        if not grade:
            return PolicyResult.deny("hard", {"grade": "not_found"})

        class_id = grade.get("class_id")
        owner_id = grade.get("teacher_id")

        if class_id and self._is_homeroom(teacher_id=teacher_id, class_id=class_id):
            return PolicyResult.ok("hard")

        if owner_id and owner_id == teacher_id:
            return PolicyResult.ok("hard")

        return PolicyResult.deny("hard", {"permission": "forbidden"})

    # -------------------------
    # LIST
    # -------------------------

    def can_list_class_grades(
        self,
        *,
        teacher_id: ObjectId,
        class_id: ObjectId,
        subject_id: Optional[ObjectId] = None,
        allow_homeroom_view_all: bool = True,
    ) -> PolicyResult:
        class_doc = self._get_class_for_guard(class_id=class_id)
        if not class_doc:
            return PolicyResult.deny("list", {"class": "not_found_or_deleted"})

        status = class_doc.get("status")
        if status in ("inactive", "archived"):
            return PolicyResult.deny("list", {"class_status": status})

        is_homeroom = (class_doc.get("homeroom_teacher_id") == teacher_id)
        if allow_homeroom_view_all and is_homeroom:
            return PolicyResult.ok("list")

        # Non-homeroom must specify subject_id
        if subject_id is None:
            return PolicyResult.deny("list", {"subject_id": "required_for_non_homeroom"})

        if not self._teacher_assigned(teacher_id=teacher_id, class_id=class_id, subject_id=subject_id):
            return PolicyResult.deny("list", {"permission": "not_assigned_for_subject"})

        return PolicyResult.ok("list")

    def build_list_filter(
        self,
        *,
        teacher_id: ObjectId,
        class_id: ObjectId,
        subject_id: Optional[ObjectId] = None,
        allow_homeroom_view_all: bool = True,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[str, Any]:
        """
        Returns a Mongo filter that ENFORCES visibility:
          - Homeroom: all grades in class (optionally subject-filtered)
          - Non-homeroom: only grades they own (teacher_id) AND for that subject (if provided)
        """
        base: Dict[str, Any] = {"class_id": class_id}

        # Homeroom sees everything in class
        if allow_homeroom_view_all and self._is_homeroom(teacher_id=teacher_id, class_id=class_id):
            if subject_id is not None:
                base["subject_id"] = subject_id
            return by_show_deleted(show_deleted, base)

        # Non-homeroom: restrict to their own grades
        base["teacher_id"] = teacher_id

        if subject_id is not None:
            base["subject_id"] = subject_id

        return by_show_deleted(show_deleted, base)