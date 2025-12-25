from __future__ import annotations

from bson import ObjectId
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult

from app.contexts.shared.lifecycle.filters import guard_not_deleted, guard_deleted
from app.contexts.shared.lifecycle.updates import (
    apply_soft_delete_update,
    apply_restore_update,
)
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException
from app.contexts.shared.lifecycle.policy_result import PolicyResult

from app.contexts.school.policies.class_policy import ClassPolicy
from app.contexts.school.errors.class_exceptions import ClassNotFoundException


class ClassLifecycleService:
    """
    Lifecycle + safety service for ClassSection.

    Responsibilities:
    - soft delete
    - restore
    - hard delete

    Non-responsibilities:
    - status changes (ACTIVE/INACTIVE/ARCHIVED) => domain/service responsibility
    """

    def __init__(self, db: Database):
        self.collection = db["classes"]
        self.policy = ClassPolicy(db)

    def _deny(self, class_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="class_section",
            entity_id=str(class_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_class(self, class_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete(class_id)
        if not can.allowed:
            self._deny(class_id, can)

        res = self.collection.update_one(
            guard_not_deleted(class_id),
            apply_soft_delete_update(actor_id),
        )
        if res.matched_count == 0:
            raise ClassNotFoundException(str(class_id))
        return res

    def restore_class(self, class_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        """
        Restore must target deleted docs.
        actor_id is accepted for parity, but only used if your apply_restore_update uses it.
        """
        can = self.policy.can_restore(class_id)
        if not can.allowed:
            self._deny(class_id, can)

        res = self.collection.update_one(
            guard_deleted(class_id),
            apply_restore_update(), 
        )
        if res.matched_count == 0:
            raise ClassNotFoundException(str(class_id))
        return res

    def hard_delete_class(self, class_id: ObjectId, actor_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete(class_id)
        if not can.allowed:
            self._deny(class_id, can)

        res = self.collection.delete_one({"_id": class_id})
        if res.deleted_count == 0:
            raise ClassNotFoundException(str(class_id))
        return res