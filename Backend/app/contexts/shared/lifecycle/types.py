from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from bson import ObjectId


def now_utc() -> datetime:
    return datetime.utcnow()


# ------------------------------------------------------------
# Lifecycle field keys (nested under "lifecycle.*")
# ------------------------------------------------------------

@dataclass(frozen=True)
class LifecycleFields:
    root: str = "lifecycle"
    created_at: str = "created_at"
    updated_at: str = "updated_at"
    deleted_at: str = "deleted_at"
    deleted_by: str = "deleted_by"
    restored_at: str = "restored_at"
    restored_by: str = "restored_by"

    def k(self, field: str) -> str:
        return f"{self.root}.{field}"


FIELDS = LifecycleFields()


# ------------------------------------------------------------
# Updates
# ------------------------------------------------------------

def apply_soft_delete_update(actor_id: ObjectId) -> Dict[str, Any]:
    n = now_utc()
    return {
        "$set": {
            FIELDS.k(FIELDS.deleted_at): n,
            FIELDS.k(FIELDS.deleted_by): actor_id,
            FIELDS.k(FIELDS.updated_at): n,
        }
    }


def apply_restore_update(actor_id: ObjectId | None = None) -> Dict[str, Any]:
    n = now_utc()
    payload: Dict[str, Any] = {
        FIELDS.k(FIELDS.deleted_at): None,
        FIELDS.k(FIELDS.deleted_by): None,
        FIELDS.k(FIELDS.updated_at): n,
    }
    if actor_id is not None:
        payload[FIELDS.k(FIELDS.restored_at)] = n
        payload[FIELDS.k(FIELDS.restored_by)] = actor_id

    return {"$set": payload}


def apply_set_is_active_update(is_active: bool, actor_id: ObjectId | None = None) -> Dict[str, Any]:
    """
    Business toggle. Keeps lifecycle audit consistent.
    - Writes "is_active" at document root (common pattern)
    - Touches lifecycle.updated_at
    - Optionally records actor_id (if you want)
    """
    n = now_utc()
    payload: Dict[str, Any] = {
        "is_active": bool(is_active),
        FIELDS.k(FIELDS.updated_at): n,
    }

    # Optional: keep a generic "updated_by" if you want it
    # If you don't have lifecycle.updated_by in your schema, remove this block.
    if actor_id is not None:
        payload[FIELDS.k("updated_by")] = actor_id

    return {"$set": payload}