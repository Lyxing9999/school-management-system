from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Literal
from bson import ObjectId

ShowDeleted = Literal["all", "active", "deleted"]


@dataclass(frozen=True)
class LifecycleFields:
    prefix: str = "lifecycle"
    created_at: str = "created_at"
    updated_at: str = "updated_at"
    deleted_at: str = "deleted_at"
    deleted_by: str = "deleted_by"

    def k(self, name: str) -> str:
        return f"{self.prefix}.{name}"


FIELDS = LifecycleFields()


def now_utc() -> datetime:
    return datetime.utcnow()


# ---------------- Filters ----------------

def not_deleted(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    q: Dict[str, Any] = {FIELDS.k(FIELDS.deleted_at): None}
    if extra:
        q.update(extra)
    return q


def active(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return not_deleted(extra)


def by_show_deleted(show: ShowDeleted, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if show == "all":
        q: Dict[str, Any] = {}
    elif show == "deleted":
        q = {FIELDS.k(FIELDS.deleted_at): {"$ne": None}}
    else:
        q = {FIELDS.k(FIELDS.deleted_at): None}

    if extra:
        q.update(extra)
    return q


# ---------------- Guards ----------------

def guard_not_deleted(entity_id: Any) -> Dict[str, Any]:
    return {"_id": entity_id, FIELDS.k(FIELDS.deleted_at): None}


def guard_deleted(entity_id: Any) -> Dict[str, Any]:
    return {"_id": entity_id, FIELDS.k(FIELDS.deleted_at): {"$ne": None}}


# ---------------- Updates ----------------

def apply_soft_delete_update(actor_id: ObjectId) -> Dict[str, Any]:
    n = now_utc()
    return {
        "$set": {
            FIELDS.k(FIELDS.deleted_at): n,
            FIELDS.k(FIELDS.deleted_by): actor_id,
            FIELDS.k(FIELDS.updated_at): n,
        }
    }


def apply_restore_update() -> Dict[str, Any]:
    n = now_utc()
    return {
        "$set": {
            FIELDS.k(FIELDS.deleted_at): None,
            FIELDS.k(FIELDS.deleted_by): None,
            FIELDS.k(FIELDS.updated_at): n,
        }
    }