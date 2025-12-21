from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId


@dataclass(frozen=True)
class LifecycleFields:
    created_at: str = "created_at"
    updated_at: str = "updated_at"
    deleted: str = "deleted"
    deleted_at: str = "deleted_at"
    deleted_by: str = "deleted_by"


FIELDS = LifecycleFields()


def now_utc() -> datetime:
    return datetime.utcnow()


def not_deleted(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    q: Dict[str, Any] = {FIELDS.deleted: {"$ne": True}}
    if extra:
        q.update(extra)
    return q


def apply_soft_delete_update(actor_id: ObjectId) -> Dict[str, Any]:
    n = now_utc()
    return {
        "$set": {
            FIELDS.deleted: True,
            FIELDS.deleted_at: n,
            FIELDS.deleted_by: actor_id,
            FIELDS.updated_at: n,
        }
    }


def apply_restore_update() -> Dict[str, Any]:
    n = now_utc()
    return {
        "$set": {
            FIELDS.deleted: False,
            FIELDS.deleted_at: None,
            FIELDS.deleted_by: None,
            FIELDS.updated_at: n,
        }
    }