from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Optional
from bson import ObjectId
from pymongo.collection import Collection


def append_history(
    collection: Collection,
    entity_id: ObjectId,
    event: str,
    actor_id: ObjectId,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    collection.update_one(
        {"_id": entity_id},
        {"$push": {"history": {
            "event": event,
            "at": datetime.now().isoformat(),
            "meta": {"actor_id": str(actor_id), **(meta or {})},
        }}}
    )


def write_audit_log(
    audit_collection: Collection,
    *,
    actor_id: ObjectId,
    entity: str,
    entity_id: ObjectId,
    action: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    audit_collection.insert_one({
        "actor_id": actor_id,
        "entity": entity,
        "entity_id": entity_id,
        "action": action,
        "meta": meta or {},
        "created_at": datetime.now(),
    })