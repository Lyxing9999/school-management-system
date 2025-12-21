from __future__ import annotations

from typing import Optional
from datetime import datetime
from bson import ObjectId
from pymongo.database import Database
from pymongo.client_session import ClientSession
from pymongo.results import UpdateResult, DeleteResult

from app.contexts.shared.lifecycle.transaction import mongo_transaction
from app.contexts.shared.lifecycle.policy_result import PolicyResult
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException
from app.contexts.shared.lifecycle.domain import now_utc 

from app.contexts.school.policies.class_policy import ClassPolicy
from app.contexts.school.errors.class_exceptions import ClassNotFoundException
from app.contexts.school.domain.class_section import ClassSectionStatus


def _sess(session: Optional[ClientSession]) -> dict:
    """Pass session only when transactions are supported."""
    return {"session": session} if session else {}




# Mongo dot-paths for embedded lifecycle dict
LC_CREATED_AT = "lifecycle.created_at"
LC_UPDATED_AT = "lifecycle.updated_at"
LC_DELETED_AT = "lifecycle.deleted_at"
LC_DELETED_BY = "lifecycle.deleted_by"

NOT_DELETED = {LC_DELETED_AT: None}
DELETED = {LC_DELETED_AT: {"$ne": None}}


def _soft_delete_update(actor_id: ObjectId) -> dict:
    n = now_utc()
    return {
        "$set": {
            LC_DELETED_AT: n,
            LC_DELETED_BY: actor_id,
            LC_UPDATED_AT: n,
        }
    }


def _restore_update() -> dict:
    n = now_utc()
    return {
        "$set": {
            LC_DELETED_AT: None,
            LC_DELETED_BY: None,
            LC_UPDATED_AT: n,
        }
    }


def _set_status_update(status: ClassSectionStatus) -> dict:
    n = now_utc()
    return {
        "$set": {
            "status": status.value,
            LC_UPDATED_AT: n,
        }
    }


class ClassLifecycleService:
    """
    Lifecycle + safety service for ClassSection.

    Responsibilities:
    - Enforce policy checks for soft/hard delete
    - Apply lifecycle state transitions (soft delete, restore)
    - Apply business status updates (ACTIVE/INACTIVE/ARCHIVED) safely
    - Raise consistent domain errors when not found
    """

    def __init__(self, db: Database):
        self.db = db
        self.collection = db.classes  
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
        """
        Soft-delete a class:
        - policy must allow
        - only applies when not already deleted
        """
        can = self.policy.can_soft_delete(class_id)
        if not can.allowed:
            self._deny(class_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                {"_id": class_id, **NOT_DELETED},
                _soft_delete_update(actor_id),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise ClassNotFoundException(class_id)
            return res

    def restore_class(self, class_id: ObjectId, actor_id: ObjectId) -> UpdateResult:
        """
        Restore a soft-deleted class.
        (Policy optional; you can add can_restore later.)
        """
        can = self.policy.can_restore(class_id)
        if not can.allowed:
            self._deny(class_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                {"_id": class_id, **DELETED},
                _restore_update(),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise ClassNotFoundException(class_id)
            return res

    def set_class_status(
        self,
        class_id: ObjectId,
        status: ClassSectionStatus | str,
        *,
        require_not_deleted: bool = True,
    ) -> UpdateResult:
        """
        Business status change (ACTIVE/INACTIVE/ARCHIVED).
        Lifecycle is unchanged; only updated_at is touched.
        """
        normalized = status if isinstance(status, ClassSectionStatus) else ClassSectionStatus(status)

        guard = {"_id": class_id}
        if require_not_deleted:
            guard.update(NOT_DELETED)

        with mongo_transaction(self.db) as session:
            res = self.collection.update_one(
                guard,
                _set_status_update(normalized),
                **_sess(session),
            )
            if res.matched_count == 0:
                raise ClassNotFoundException(class_id)
            return res

    def hard_delete_class(self, class_id: ObjectId, actor_id: ObjectId) -> DeleteResult:
        """
        Permanent delete:
        - policy must allow
        - use with care (usually only after soft delete)
        """
        can = self.policy.can_hard_delete(class_id)
        if not can.allowed:
            self._deny(class_id, can)

        with mongo_transaction(self.db) as session:
            res = self.collection.delete_one({"_id": class_id}, **_sess(session))
            if res.deleted_count == 0:
                raise ClassNotFoundException(class_id)
            return res