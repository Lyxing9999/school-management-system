from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from bson import ObjectId
from .filters import FIELDS


def now_utc() -> datetime:
    return datetime.utcnow()


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


def apply_touch_update() -> Dict[str, Any]:
    return {"$set": {FIELDS.k(FIELDS.updated_at): now_utc()}}


def apply_set_status_update(status: str | Enum) -> Dict[str, Any]:
    n = now_utc()
    value = status.value if isinstance(status, Enum) else status
    return {"$set": {"status": value, FIELDS.k(FIELDS.updated_at): n}}