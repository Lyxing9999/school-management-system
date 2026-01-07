from __future__ import annotations

from typing import Any, Dict, Optional, Union, Literal
from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import by_show_deleted, not_deleted, ShowDeleted
from app.contexts.shared.lifecycle.policy_result import PolicyResult


class GradePolicy:
    """
    Policy aligned with your CURRENT schema (no new fields):
      grades: { student_id, class_id, subject_id, teacher_id, type, term, score, lifecycle... }
      teacher_subject_assignments: { teacher_id, class_id, subject_id, lifecycle... }
      classes: { homeroom_teacher_id, status, lifecycle... }

    Target behavior:
      - Create grade: ONLY assigned subject-teacher can create (homeroom override optional).
      - Update/Delete grade:
          * Homeroom teacher (of that class) can manage all grades in that class (optional).
          * Non-homeroom (subject teacher) can manage ONLY grades they created (grade.teacher_id == actor).
      - List grades:
          * Homeroom can view all grades in class.
          * Non-homeroom can view ONLY their own grades in class (and typically for selected subject).
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

    def _is_homeroom(self, *, teacher_id: ObjectId, class_id: ObjectId) -> bool:
        cls = self.classes.find_one(
            not_deleted({"_id": class_id}),
            {"_id": 1, "homeroom_teacher_id": 1, "status": 1},
        )
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

    def _get_class_for_guard(self, *, class_id: ObjectId) -> dict | None:
        return self.classes.find_one(
            not_deleted({"_id": class_id}),
            {"_id": 1, "homeroom_teacher_id": 1, "status": 1},
        )

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
        class_id: ObjectId | None = None,
        term: str | None = None,
        grade_type: str | None = None,
        require_student_in_class: bool = False,
        prevent_duplicate: bool = False,
        allow_homeroom_override: bool = False,
    ) -> PolicyResult:
        blockers: Dict[str, Any] = {}

        # Subject must exist + active
        subj = self.subjects.find_one(
            not_deleted({"_id": subject_id}),
            {"_id": 1, "is_active": 1},
        )
        if not subj:
            return PolicyResult.deny("create", {"subject": "not_found_or_deleted"})
        if subj.get("is_active") is False:
            return PolicyResult.deny("create", {"subject": "inactive"})

        # Class must exist + active
        class_doc = self._get_class_for_guard(class_id=class_id)
        if not class_doc:
            return PolicyResult.deny("create", {"class": "not_found_or_deleted"})

        status = class_doc.get("status")
        if status in ("inactive", "archived"):
            return PolicyResult.deny("create", {"class_status": status})

        # Authorization:
        # Default: assigned subject-teacher only.
        # Optional: allow homeroom override (NOT recommended if homeroom doesn't teach all subjects).
        is_homeroom = (class_doc.get("homeroom_teacher_id") == teacher_id)
        if not (allow_homeroom_override and is_homeroom):
            if not self._teacher_assigned(teacher_id=teacher_id, class_id=class_id, subject_id=subject_id):
                return PolicyResult.deny("create", {"permission": "not_assigned_for_subject"})

        # Optional: student must be currently in class
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

        # Duplicate prevention (WARNING: blocks multiple exams with current schema)
        if prevent_duplicate:
            q: Dict[str, Any] = not_deleted({
                "student_id": student_id,
                "subject_id": subject_id,
                "term": term,
            })

            if class_id is not None:
                q["class_id"] = class_id

            if grade_type is not None:
                q["type"] = grade_type

            existing = self.grades.find_one(q, {"_id": 1})
            if existing:
                return PolicyResult.deny("create", {
                    "duplicate": "grade_already_exists",
                    "existing_grade_id": str(existing["_id"]),
                })
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
        allow_assigned_subject_teacher: bool = True,
        allow_owner_fallback: bool = True,  # keep if you want “creator can still edit”
    ) -> PolicyResult:
        grade = self._get_grade_for_guard(grade_id=grade_id)
        if not grade:
            return PolicyResult.deny("modify", {"grade": "not_found_or_deleted"})

        class_id: ObjectId | None = grade.get("class_id")
        subject_id: ObjectId | None = grade.get("subject_id")
        owner_id: ObjectId | None = grade.get("teacher_id")

        # 1) Homeroom can manage all grades in their class
        if allow_homeroom_manage_all and class_id and self._is_homeroom(
            teacher_id=teacher_id, class_id=class_id
        ):
            return PolicyResult.ok("modify")

        # 2) Assigned subject teacher can manage grades for that subject+class
        if allow_assigned_subject_teacher and class_id and subject_id:
            if self._teacher_assigned(
                teacher_id=teacher_id,
                class_id=class_id,
                subject_id=subject_id,
            ):
                return PolicyResult.ok("modify")

        # 3) Optional: grade creator can still edit their own grades
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
    # LISTING (the missing piece)
    # -------------------------

    def can_list_class_grades(
        self,
        *,
        teacher_id: ObjectId,
        class_id: ObjectId,
        subject_id: Optional[ObjectId] = None,
        allow_homeroom_view_all: bool = True,
    ) -> PolicyResult:
        """
        List rule:
          - Homeroom can view all grades in class.
          - Non-homeroom:
              * must provide subject_id
              * must be assigned to that subject in that class
              * will only be allowed to see THEIR OWN grades (enforced in list filter)
        """
        class_doc = self._get_class_for_guard(class_id=class_id)
        if not class_doc:
            return PolicyResult.deny("list", {"class": "not_found_or_deleted"})

        status = class_doc.get("status")
        if status in ("inactive", "archived"):
            return PolicyResult.deny("list", {"class_status": status})

        is_homeroom = (class_doc.get("homeroom_teacher_id") == teacher_id)
        if allow_homeroom_view_all and is_homeroom:
            return PolicyResult.ok("list")

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
        base: Dict[str, Any] = {"class_id": class_id}

        # Homeroom sees all subjects
        if allow_homeroom_view_all and self._is_homeroom(teacher_id=teacher_id, class_id=class_id):
            if subject_id is not None:
                base["subject_id"] = subject_id
            return by_show_deleted(show_deleted, base)


        if subject_id is not None:
            base["subject_id"] = subject_id
        return by_show_deleted(show_deleted, base)