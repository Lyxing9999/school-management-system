from dataclasses import dataclass
from typing import Any, Dict, Optional, Literal
from datetime import datetime, time, timedelta

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



def build_date_range(
    field_key: str,
    *,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    end_exclusive: bool = True,
) -> Dict[str, Any]:

    if not date_from and not date_to:
        return {}

    q: Dict[str, Any] = {}

    if date_from:
        q["$gte"] = date_from

    if date_to:
        if date_to.time() == time.min:
            date_to = date_to + timedelta(days=1)

        q["$lt" if end_exclusive else "$lte"] = date_to

    return {field_key: q} if q else {}



def guard_not_deleted(entity_id: Any) -> Dict[str, Any]:
    return {"_id": entity_id, FIELDS.k(FIELDS.deleted_at): None}


def guard_deleted(entity_id: Any) -> Dict[str, Any]:
    return {"_id": entity_id, FIELDS.k(FIELDS.deleted_at): {"$ne": None}}