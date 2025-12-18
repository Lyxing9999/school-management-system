from __future__ import annotations

from typing import Any, Dict, Optional, Literal
from app.contexts.shared.lifecycle.types import FIELDS, Status

ShowDeleted = Literal["all", "active", "deleted"]
ShowStatus = Literal["all", "active", "inactive", "suspended"]


def not_deleted(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Default for most queries.
    Includes docs where deleted is False OR missing.
    """
    q: Dict[str, Any] = {FIELDS.deleted: {"$ne": True}}
    if extra:
        q.update(extra)
    return q


def active(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Operational "active" records only.
    status=active AND deleted != true
    """
    q: Dict[str, Any] = {
        FIELDS.status: Status.ACTIVE.value,
        FIELDS.deleted: {"$ne": True},
    }
    if extra:
        q.update(extra)
    return q


def by_show_deleted(show: ShowDeleted, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Admin filter helper:
      - all: no delete filter
      - active: deleted != true
      - deleted: deleted == true
    """
    if show == "all":
        q: Dict[str, Any] = {}
    elif show == "deleted":
        q = {FIELDS.deleted: True}
    else:
        q = {FIELDS.deleted: {"$ne": True}}

    if extra:
        q.update(extra)
    return q


def by_show_status(show: ShowStatus, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Optional if you want admin status filters too.
    """
    if show == "all":
        q: Dict[str, Any] = {}
    else:
        q = {FIELDS.status: show}

    if extra:
        q.update(extra)
    return q


# --------- Optional guard filters for safe updates ---------

def guard_not_deleted(entity_id: Any) -> Dict[str, Any]:
    """
    Useful for preventing updates on deleted docs:
    update_one(guard_not_deleted(id), {"$set": ...})
    """
    return {"_id": entity_id, FIELDS.deleted: {"$ne": True}}


def guard_active(entity_id: Any) -> Dict[str, Any]:
    """
    Prevent updates unless entity is active and not deleted.
    """
    return {"_id": entity_id, FIELDS.status: Status.ACTIVE.value, FIELDS.deleted: {"$ne": True}}