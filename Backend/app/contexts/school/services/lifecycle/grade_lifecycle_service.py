from bson import ObjectId
from pymongo.database import Database
from pymongo.results import UpdateResult, DeleteResult

from app.contexts.shared.lifecycle.filters import guard_not_deleted, guard_deleted
from app.contexts.shared.lifecycle.types import (
    apply_soft_delete_update,
    apply_restore_update,
)
from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException

from app.contexts.school.policies.grade_policy import GradePolicy
from app.contexts.school.errors.grade_exceptions import GradeNotFoundException


class GradeLifecycleService:
    """
    Lifecycle + safety service for GradeRecord.

    Responsibilities:
    - soft delete / restore / hard delete
    - policy checks before destructive actions

    No transactions: each method updates only ONE document.
    """

    def __init__(self, db: Database):
        self.collection = db["grades"]
        self.policy = GradePolicy(db)

    def _deny(self, grade_id: ObjectId, can: PolicyResult) -> None:
        raise LifecyclePolicyDeniedException(
            entity="grade",
            entity_id=str(grade_id),
            mode=can.mode,
            reasons=can.reasons,
            recommended=can.recommended,
        )

    def soft_delete_grade(
        self,
        grade_id: ObjectId,
        actor_id: ObjectId,
    ) -> UpdateResult:
        """
        Soft delete a grade (sets lifecycle.deleted_at/by + updated_at).
        """
        can = self.policy.can_soft_delete(grade_id, actor_id)
        if not can.allowed:
            self._deny(grade_id, can)

        res = self.collection.update_one(
            guard_not_deleted(grade_id),
            apply_soft_delete_update(actor_id),
        )
        if res.matched_count == 0:
            raise GradeNotFoundException(str(grade_id))
        return res

    def restore_grade(
        self,
        grade_id: ObjectId,
        actor_id: ObjectId | None = None,
    ) -> UpdateResult:
        """
        Restore a soft-deleted grade (sets lifecycle.deleted_at/by back to None).
        actor_id is optional depending on your apply_restore_update signature.
        """
        can = self.policy.can_restore(grade_id)
        if not can.allowed:
            self._deny(grade_id, can)

        res = self.collection.update_one(
            guard_deleted(grade_id),
            apply_restore_update(actor_id),
        )
        if res.matched_count == 0:
            raise GradeNotFoundException(str(grade_id))
        return res

    def hard_delete_grade(
        self,
        grade_id: ObjectId,
        actor_id: ObjectId,
    ) -> DeleteResult:
        """
        Hard delete a grade (physical remove).
        Typically admin-only.
        """
        can = self.policy.can_hard_delete(grade_id)
        if not can.allowed:
            self._deny(grade_id, can)

        res = self.collection.delete_one({"_id": grade_id})
        if res.deleted_count == 0:
            raise GradeNotFoundException(str(grade_id))
        return res