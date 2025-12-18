from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass(frozen=True)
class LifecycleFields:
    status: str = "status"
    deleted: str = "deleted"
    deleted_at: str = "deleted_at"
    deleted_by: str = "deleted_by"
    updated_at: str = "updated_at"


FIELDS = LifecycleFields()


def now_utc() -> datetime:
    return datetime.utcnow()


def active_filter(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    q = {FIELDS.status: Status.ACTIVE.value, FIELDS.deleted: {"$ne": True}}
    if extra:
        q.update(extra)
    return q


def apply_soft_delete_update(actor_id: ObjectId) -> Dict[str, Any]:
    n = now_utc()
    return {
        "$set": {
            FIELDS.status: Status.INACTIVE.value,
            FIELDS.deleted: True,
            FIELDS.deleted_at: n,
            FIELDS.deleted_by: actor_id,
            FIELDS.updated_at: n,
        }
    }


def apply_restore_update(actor_id: ObjectId) -> Dict[str, Any]:
    n = now_utc()
    return {
        "$set": {
            FIELDS.status: Status.ACTIVE.value,
            FIELDS.deleted: False,
            FIELDS.deleted_at: None,
            FIELDS.deleted_by: None,
            FIELDS.updated_at: n,
        }
    }


def apply_set_status_update(status: Status) -> Dict[str, Any]:
    n = now_utc()
    return {"$set": {FIELDS.status: status.value, FIELDS.updated_at: n}}