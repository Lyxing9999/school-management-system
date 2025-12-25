from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Literal

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
        # safer when old docs may not have lifecycle.deleted_at
        q = {FIELDS.k(FIELDS.deleted_at): {"$exists": True, "$ne": None}}
    else:
        q = {FIELDS.k(FIELDS.deleted_at): None}

    if extra:
        q.update(extra)
    return q





def guard_not_deleted(entity_id: Any) -> Dict[str, Any]:
    return {"_id": entity_id, FIELDS.k(FIELDS.deleted_at): None}


def guard_deleted(entity_id: Any) -> Dict[str, Any]:
    return {"_id": entity_id, FIELDS.k(FIELDS.deleted_at): {"$ne": None}}