# contexts/student/services/lifecycle/student_lifecycle_service.py
from __future__ import annotations

from typing import Optional, Any, Dict
from bson import ObjectId
from pymongo.database import Database
from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult, DeleteResult

from contexts.shared.lifecycle.types import (
    apply_soft_delete_update,
    apply_restore_update,
)
from contexts.shared.lifecycle.audit import append_history
from contexts.shared.lifecycle.transaction import mongo_transaction
from contexts.shared.lifecycle.policy_result import PolicyResult
from contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException

from contexts.student.policies.student_policy import StudentPolicy
from contexts.student.errors.student_exceptions import StudentNotFoundException 
from contexts.iam.error.iam_exception import NotFoundUserException          


from contexts.student.domain.student import StudentStatus as Status



LIFECYCLE_NOT_DELETED = {"lifecycle.deleted_at": None}
LIFECYCLE_DELETED = {"lifecycle.deleted_at": {"$ne": None}}


def _sess(session: Optional[ClientSession]) -> Dict[str, Any]:
    return {"session": session} if session else {}


class StudentLifecycleService:
    """
    Trusted writer for STUDENT lifecycle.

    Uses transaction because operations touch multiple collections:
      - students
      - iam (or users) account document
      - classes (optional: enrolled_count recompute)

    Important:
      - Domain handles "business status" semantics.
      - Lifecycle handles delete/restore/hard-delete + audit + safety policy.
    """

    def __init__(self, db: Database):
        self.db = db
        self.students = db.students
        self.iam = db.iam            # aligns with your IAMLifecycleService using db.iam
        self.classes = db.classes
        self.policy = StudentPolicy(db)

    # ----------------------------
    # Policy deny helper
    # ----------------------------
    def _deny(self, student_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="student",
            entity_id=str(student_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    # ----------------------------
    # Utilities
    # ----------------------------
    def _recompute_enrolled_count(self, class_id: ObjectId, *, session: Optional[ClientSession]) -> None:
        """
        Safe recalculation to prevent drift.
        This assumes student.current_class_id is the source of truth.
        """
        count = self.students.count_documents(
            {"current_class_id": class_id, **LIFECYCLE_NOT_DELETED},
            **_sess(session),
        )
        # If you have lifecycle.updated_at, you can also set it here.
        self.classes.update_one(
            {"_id": class_id, **LIFECYCLE_NOT_DELETED},
            {"$set": {"enrolled_count": int(count)}},
            **_sess(session),
        )

    # ============================================================
    # Status change (business-level)
    # ============================================================
    def set_status(self, student_id: ObjectId, status: Status, actor_id: ObjectId) -> UpdateResult:
        """
        Status is NOT delete/restore; it is a business state (Active/Inactive/etc).
        Keep it separate from lifecycle.deleted_at semantics.
        """
        # Optional: enforce policy.can_change_status(student_id, status) if you have it
        # can = self.policy.can_change_status(student_id, status)
        # if not can.allowed: self._deny(student_id, can)

        res = self.students.update_one(
            {"_id": student_id, **LIFECYCLE_NOT_DELETED},
            apply_set_status_update(status),
        )
        if res.matched_count == 0:
            raise StudentNotFoundException(str(student_id))

        append_history(
            self.students,
            student_id,
            "STUDENT_STATUS_CHANGED",
            actor_id,
            {"status": getattr(status, "value", status)},
        )
        return res

    # ============================================================
    # Soft delete (default)
    # ============================================================
    def soft_delete(self, student_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete(student_id)
        if not can.allowed:
            self._deny(student_id, can)

        with mongo_transaction(self.db) as session:
            student = self.students.find_one(
                {"_id": student_id, **LIFECYCLE_NOT_DELETED},
                {"_id": 1, "user_id": 1, "current_class_id": 1},
                **_sess(session),
            )
            if not student:
                raise StudentNotFoundException(str(student_id))

            user_id: ObjectId = student["user_id"]
            current_class_id: Optional[ObjectId] = student.get("current_class_id")

            
            stu_res = self.students.update_one(
                {"_id": student_id, **LIFECYCLE_NOT_DELETED},
                apply_soft_delete_update(actor_id),
                **_sess(session),
            )
            if stu_res.matched_count == 0:
                raise StudentNotFoundException(str(student_id))


            if current_class_id:
                self.students.update_one(
                    {"_id": student_id},
                    {"$set": {"current_class_id": None}},
                    **_sess(session),
                )
                self._recompute_enrolled_count(current_class_id, session=session)


            iam_res = self.iam.update_one(
                {"_id": user_id, **LIFECYCLE_NOT_DELETED},
                apply_soft_delete_update(actor_id),
                **_sess(session),
            )
            if iam_res.matched_count == 0:
             
                raise NotFoundUserException(str(user_id))

            append_history(self.students, student_id, "STUDENT_SOFT_DELETED", actor_id)

            return stu_res

    # ============================================================
    # Restore
    # ============================================================
    def restore(self, student_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_restore(student_id)
        if not can.allowed:
            self._deny(student_id, can)

        with mongo_transaction(self.db) as session:
            student = self.students.find_one(
                {"_id": student_id, **LIFECYCLE_DELETED},
                {"_id": 1, "user_id": 1},
                **_sess(session),
            )
            if not student:
                raise StudentNotFoundException(str(student_id))

            user_id: ObjectId = student["user_id"]

    
            stu_res = self.students.update_one(
                {"_id": student_id, **LIFECYCLE_DELETED},
                apply_restore_update(actor_id),
                **_sess(session),
            )
            if stu_res.matched_count == 0:
                raise StudentNotFoundException(str(student_id))

 
            iam_res = self.iam.update_one(
                {"_id": user_id, **LIFECYCLE_DELETED},
                apply_restore_update(actor_id),
                **_sess(session),
            )
            if iam_res.matched_count == 0:
                raise NotFoundUserException(str(user_id))

            append_history(self.students, student_id, "STUDENT_RESTORED", actor_id)
            return stu_res

    # ============================================================
    # Hard delete (rare)
    # ============================================================
    def hard_delete(self, student_id: ObjectId, actor_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete(student_id)
        if not can.allowed:
            self._deny(student_id, can)

        with mongo_transaction(self.db) as session:
            student = self.students.find_one(
                {"_id": student_id},
                {"_id": 1, "user_id": 1, "current_class_id": 1},
                **_sess(session),
            )
            if not student:
                raise StudentNotFoundException(str(student_id))

            user_id: ObjectId = student["user_id"]
            current_class_id: Optional[ObjectId] = student.get("current_class_id")


            res = self.students.delete_one({"_id": student_id}, **_sess(session))
            if res.deleted_count == 0:
                raise StudentNotFoundException(str(student_id))

            if current_class_id:
                self._recompute_enrolled_count(current_class_id, session=session)

            # hard delete IAM user ONLY if your IAM policy allows it
            # NOTE: your IAMLifecycleService requires actor_id; we keep same signature style here.
            iam_res = self.iam.delete_one({"_id": user_id}, **_sess(session))
            # If you want strictness:
            # if iam_res.deleted_count == 0: raise NotFoundUserException(str(user_id))

            append_history(self.students, student_id, "STUDENT_HARD_DELETED", actor_id)
            return res