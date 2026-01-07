from bson import ObjectId
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult

from app.contexts.shared.lifecycle.filters import guard_not_deleted, guard_deleted
from app.contexts.shared.lifecycle.types import (
    apply_soft_delete_update,
    apply_restore_update,
    apply_set_is_active_update,
)
from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException

from app.contexts.school.policies.subject_policy import SubjectPolicy
from app.contexts.school.errors.subject_exceptions import SubjectNotFoundException


class SubjectLifecycleService:
    def __init__(self, db: Database):
        self.collection = db["subjects"]
        self.policy = SubjectPolicy(db)

    def _deny(self, subject_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="subject",
            entity_id=str(subject_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_subject(self, subject_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_soft_delete(subject_id)
        if not can.allowed:
            self._deny(subject_id, can)

        res = self.collection.update_one(
            guard_not_deleted(subject_id),
            apply_soft_delete_update(actor_id),
        )
        if res.matched_count == 0:
            raise SubjectNotFoundException(str(subject_id))
        return res

    def restore_subject(self, subject_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        can = self.policy.can_restore(subject_id)
        if not can.allowed:
            self._deny(subject_id, can)

        res = self.collection.update_one(
            guard_deleted(subject_id),
            apply_restore_update(actor_id),
        )
        if res.matched_count == 0:
            raise SubjectNotFoundException(str(subject_id))
        return res

    def set_subject_active(self, subject_id: ObjectId, is_active: bool, actor_id: ObjectId) -> UpdateResult:
        res = self.collection.update_one(
            guard_not_deleted(subject_id),
            apply_set_is_active_update(is_active, actor_id),
        )
        if res.matched_count == 0:
            raise SubjectNotFoundException(str(subject_id))
        return res

    def hard_delete_subject(self, subject_id: ObjectId, actor_id: ObjectId) -> DeleteResult:
        can = self.policy.can_hard_delete(subject_id)
        if not can.allowed:
            self._deny(subject_id, can)

        res = self.collection.delete_one({"_id": subject_id})
        if res.deleted_count == 0:
            raise SubjectNotFoundException(str(subject_id))
        return res