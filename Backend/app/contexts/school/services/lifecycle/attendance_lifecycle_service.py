
from bson import ObjectId
from pymongo.database import Database
from pymongo.results import DeleteResult, UpdateResult

from app.contexts.shared.lifecycle.filters import guard_deleted, guard_not_deleted
from app.contexts.shared.lifecycle.types import apply_restore_update, apply_soft_delete_update
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException
from app.contexts.shared.lifecycle.policy_result import PolicyResult

from app.contexts.school.policies.attendance_policy import AttendancePolicy
from app.contexts.school.errors.attendance_exceptions import AttendanceNotFoundException


class AttendanceLifecycleService:
    """
    Lifecycle + safety service for AttendanceRecord.

    Scope:
    - soft delete / restore / hard delete
    - policy checks before destructive actions
    """

    def __init__(self, db: Database):
        self.collection = db["attendance"]
        self.policy = AttendancePolicy(db)

    def _deny(self, attendance_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="attendance",
            entity_id=str(attendance_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_attendance(self, attendance_id: ObjectId, actor_teacher_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete(attendance_id=attendance_id, actor_teacher_id=actor_teacher_id)
        if not can.allowed:
            self._deny(attendance_id, can)

        res = self.collection.update_one(
            guard_not_deleted(attendance_id),
            apply_soft_delete_update(actor_teacher_id),
        )
        if res.matched_count == 0:
            raise AttendanceNotFoundException(str(attendance_id))
        return res

    def restore_attendance(self, attendance_id: ObjectId, actor_teacher_id: ObjectId | None = None) -> UpdateResult:
        can = self.policy.can_restore(attendance_id)
        if not can.allowed:
            self._deny(attendance_id, can)

        res = self.collection.update_one(
            guard_deleted(attendance_id),
            apply_restore_update(actor_teacher_id),
        )
        if res.matched_count == 0:
            raise AttendanceNotFoundException(str(attendance_id))
        return res

    def hard_delete_attendance(self, attendance_id: ObjectId, actor_teacher_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete(attendance_id)
        if not can.allowed:
            self._deny(attendance_id, can)

        res = self.collection.delete_one({"_id": attendance_id})
        if res.deleted_count == 0:
            raise AttendanceNotFoundException(str(attendance_id))
        return res