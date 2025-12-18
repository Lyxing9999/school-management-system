from __future__ import annotations
from typing import Optional
from bson import ObjectId
from pymongo.database import Database

from contexts.shared.lifecycle.types import (
    apply_soft_delete_update,
    apply_restore_update,
    apply_set_status_update,
    Status,
)
from contexts.shared.lifecycle.audit import append_history
from contexts.shared.lifecycle.transaction import mongo_transaction

from contexts.student.policies.student_policy import StudentPolicy
from contexts.iam.services.iam_lifecycle_service import IAMLifecycleService
from contexts.school.services.class_lifecycle_service import ClassLifecycleService


class StudentLifecycleService:
    """
    Single trusted writer for student lifecycle:
    - set_status
    - soft_delete (default)
    - restore
    - hard_delete (rare)
    """

    def __init__(self, db: Database):
        self.db = db
        self.students = db.students
        self.policy = StudentPolicy(db)

        # cross-context dependencies
        self.iam_lifecycle = IAMLifecycleService(db)
        self.class_lifecycle = ClassLifecycleService(db)

    def set_status(self, student_id: ObjectId, status: Status, actor_id: ObjectId) -> None:
        self.students.update_one({"_id": student_id}, apply_set_status_update(status))
        append_history(self.students, student_id, "STUDENT_STATUS_CHANGED", actor_id, {"status": status.value})

    def soft_delete(self, student_id: ObjectId, actor_id: ObjectId) -> None:
        can = self.policy.can_soft_delete(student_id)
        if not can.allowed:
            raise Exception(f"Cannot soft delete student: {can.reasons}")  # replace with your AppBaseException

        with mongo_transaction(self.db) as session:
            student = self.students.find_one({"_id": student_id}, session=session) if session else self.students.find_one({"_id": student_id})
            if not student:
                return

            user_id: ObjectId = student["user_id"]
            current_class_id: Optional[ObjectId] = student.get("current_class_id")

            # 1) student lifecycle fields
            if session:
                self.students.update_one({"_id": student_id}, apply_soft_delete_update(actor_id), session=session)
            else:
                self.students.update_one({"_id": student_id}, apply_soft_delete_update(actor_id))

            # 2) disable IAM user
            if session:
                self.db.users.update_one({"_id": user_id}, apply_soft_delete_update(actor_id), session=session)
            else:
                self.db.users.update_one({"_id": user_id}, apply_soft_delete_update(actor_id))

            # 3) detach membership (recommended source-of-truth: student.current_class_id)
            if current_class_id:
                if session:
                    self.students.update_one({"_id": student_id}, {"$set": {"current_class_id": None}}, session=session)
                else:
                    self.students.update_one({"_id": student_id}, {"$set": {"current_class_id": None}})

                # recompute enrolled_count (safe, prevents drift)
                self.class_lifecycle.recompute_enrolled_count(current_class_id)

            # 4) history
            append_history(self.students, student_id, "STUDENT_SOFT_DELETED", actor_id)

    def restore(self, student_id: ObjectId, actor_id: ObjectId) -> None:
        can = self.policy.can_restore(student_id)
        if not can.allowed:
            raise Exception(f"Cannot restore student: {can.reasons}")

        student = self.students.find_one({"_id": student_id})
        if not student:
            return

        user_id: ObjectId = student["user_id"]

        # restore both student + user (do NOT auto re-enroll; keep that explicit)
        self.students.update_one({"_id": student_id}, apply_restore_update(actor_id))
        self.db.users.update_one({"_id": user_id}, apply_restore_update(actor_id))

        append_history(self.students, student_id, "STUDENT_RESTORED", actor_id)

    def hard_delete(self, student_id: ObjectId, actor_id: ObjectId) -> None:
        can = self.policy.can_hard_delete(student_id)
        if not can.allowed:
            raise Exception(f"Cannot hard delete student: {can.reasons}")

        student = self.students.find_one({"_id": student_id})
        if not student:
            return

        user_id: ObjectId = student["user_id"]

        with mongo_transaction(self.db) as session:
            if session:
                self.students.delete_one({"_id": student_id}, session=session)
                # hard delete user only if not referenced elsewhere (IAMPolicy enforces)
                self.iam_lifecycle.hard_delete_user(user_id)
            else:
                self.students.delete_one({"_id": student_id})
                self.iam_lifecycle.hard_delete_user(user_id)