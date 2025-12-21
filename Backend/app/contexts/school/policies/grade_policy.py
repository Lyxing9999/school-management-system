from __future__ import annotations

from typing import Any, Dict, Optional

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.types import not_deleted


class GradePolicy:
    """
    Policy for grade operations (create/update/delete guards).

    Philosophy:
    - Domain validates internal invariants (score range, enum type, etc.)
    - Policy validates cross-aggregate rules using DB reads:
        * subject exists + not deleted
        * class exists + not deleted (optional)
        * teacher is allowed (simple: must be class teacher)
        * student enrollment (optional)
        * duplicates (optional, depends on your business)
    """

    def __init__(self, db: Database):
        self.db = db
        self.subjects = db.subjects
        self.classes = db.classes
        self.students = db.students
        self.grades = db.grades

    # ------------------------------------------------------------
    # Create guards
    # ------------------------------------------------------------
    def can_create(
        self,
        *,
        student_id: ObjectId,
        subject_id: ObjectId,
        teacher_id: ObjectId,
        class_id: ObjectId | None = None,
        term: str | None = None,
        # Optional toggle checks
        require_student_in_class: bool = False,
        prevent_duplicate: bool = False,
    ) -> PolicyResult:
        blockers: Dict[str, Any] = {}

        # 1) Subject must exist + not deleted
        subj = self.subjects.find_one(
            {"_id": subject_id, **not_deleted()},
            {"_id": 1, "is_active": 1},
        )
        if not subj:
            blockers["subject"] = "not_found_or_deleted"
            return PolicyResult.deny("create", blockers)

        # Optional: subject active flag (if you use is_active instead of lifecycle)
        if subj.get("is_active") is False:
            blockers["subject"] = "inactive"
            return PolicyResult.deny("create", blockers)

        # 2) If class is provided: class must exist + not deleted
        class_doc = None
        if class_id is not None:
            class_doc = self.classes.find_one(
                {"_id": class_id, **not_deleted()},
                {"_id": 1, "teacher_id": 1, "status": 1},
            )
            if not class_doc:
                blockers["class"] = "not_found_or_deleted"
                return PolicyResult.deny("create", blockers)

            # Optional: block grading if class status is not active
            # (adjust values to your ClassSectionStatus)
            status = class_doc.get("status")
            if status in ("inactive", "archived"):
                blockers["class_status"] = status
                return PolicyResult.deny("create", blockers)

            # 3) Teacher must be the class teacher (simple rule)
            if class_doc.get("teacher_id") != teacher_id:
                blockers["teacher"] = "not_class_teacher"
                return PolicyResult.deny("create", blockers)

            # 4) Optional: student must be enrolled in that class
            if require_student_in_class:
                stu = self.students.find_one(
                    {"_id": student_id, **not_deleted()},
                    {"_id": 1, "current_class_id": 1},
                )
                if not stu:
                    blockers["student"] = "not_found_or_deleted"
                    return PolicyResult.deny("create", blockers)

                if stu.get("current_class_id") != class_id:
                    blockers["enrollment"] = "student_not_in_class"
                    blockers["student_current_class_id"] = (
                        str(stu.get("current_class_id")) if stu.get("current_class_id") else None
                    )
                    return PolicyResult.deny("create", blockers)

        # 5) Optional: prevent duplicates (define what “duplicate” means for you)
        # Example: 1 grade per (student, subject, class, term, type?) — you can change later.
        if prevent_duplicate:
            q: Dict[str, Any] = {
                "student_id": student_id,
                "subject_id": subject_id,
                **not_deleted({"term": term}),
            }
            if class_id is not None:
                q["class_id"] = class_id

            existing = self.grades.find_one(q, {"_id": 1})
            if existing:
                blockers["duplicate"] = "grade_already_exists"
                blockers["existing_grade_id"] = str(existing["_id"])
                return PolicyResult.deny("create", blockers)

        return PolicyResult.ok("create")

    # ------------------------------------------------------------
    # Update guards (simple version)
    # ------------------------------------------------------------
    def can_update(self, grade_id: ObjectId) -> PolicyResult:
        # Existence + not deleted
        exists = self.grades.count_documents({"_id": grade_id, **not_deleted()})
        if exists == 0:
            return PolicyResult.deny("update", {"grade": "not_found_or_deleted"})
        return PolicyResult.ok("update")

    # ------------------------------------------------------------
    # Soft delete guards
    # ------------------------------------------------------------
    def can_soft_delete(self, grade_id: ObjectId) -> PolicyResult:
        exists = self.grades.count_documents({"_id": grade_id, **not_deleted()})
        if exists == 0:
            return PolicyResult.deny("soft", {"grade": "not_found_or_deleted"})
        return PolicyResult.ok("soft")

    # ------------------------------------------------------------
    # Hard delete guards (recommended: admin only + rare)
    # ------------------------------------------------------------
    def can_hard_delete(self, grade_id: ObjectId) -> PolicyResult:
        # Hard delete should usually require it already be soft-deleted, but optional.
        exists = self.grades.count_documents({"_id": grade_id})
        if exists == 0:
            return PolicyResult.deny("hard", {"grade": "not_found"})
        return PolicyResult.ok("hard")