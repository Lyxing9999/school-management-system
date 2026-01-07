from bson import ObjectId
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult

from app.contexts.shared.lifecycle.filters import guard_not_deleted, guard_deleted
from app.contexts.shared.lifecycle.types import apply_soft_delete_update, apply_restore_update
from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException

from app.contexts.school.policies.schedule_policy import SchedulePolicy
from app.contexts.school.errors.schedule_exceptions import ScheduleNotFoundException


class ScheduleLifecycleService:
    """
    Lifecycle + safety service for ScheduleSlot.

    Scope:
    - soft delete / restore / hard delete
    - policy checks before destructive actions

    No transactions here because each method writes only ONE document.
    """

    def __init__(self, db: Database):
        self.collection = db["schedules"]
        self.policy = SchedulePolicy(db)

    def _deny(self, slot_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="schedule_slot",
            entity_id=str(slot_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_slot(self, slot_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete(slot_id)
        if not can.allowed:
            self._deny(slot_id, can)

        res = self.collection.update_one(
            guard_not_deleted(slot_id),
            apply_soft_delete_update(actor_id),
        )
        if res.matched_count == 0:
            raise ScheduleNotFoundException(str(slot_id))
        return res

    def restore_slot(self, slot_id: ObjectId, actor_id: ObjectId | None = None) -> UpdateResult:
        can = self.policy.can_restore(slot_id)
        if not can.allowed:
            self._deny(slot_id, can)

        res = self.collection.update_one(
            guard_deleted(slot_id),
            apply_restore_update(actor_id),  
        )
        if res.matched_count == 0:
            raise ScheduleNotFoundException(str(slot_id))
        return res

    def hard_delete_slot(self, slot_id: ObjectId, actor_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete(slot_id)
        if not can.allowed:
            self._deny(slot_id, can)

        res = self.collection.delete_one({"_id": slot_id})
        if res.deleted_count == 0:
            raise ScheduleNotFoundException(str(slot_id))
        return res