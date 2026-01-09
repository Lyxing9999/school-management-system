import datetime as dt
from typing import Any, Dict, Optional
from pymongo.database import Database

from app.contexts.notifications.realtime.emitter import emit_notification
from app.contexts.notifications.read_models.notification_read_model import NotificationReadModel
from app.contexts.notifications.utils.normalize import normalize_value


def _iso(v):
    if v is None:
        return None
    try:
        return v.isoformat()
    except Exception:
        return str(v)


class NotificationService:
    def __init__(self, db: Database):
        self.db = db
        self.col = db["notifications"]
        self.read_model = NotificationReadModel(db)

    def create_for_user(
        self,
        *,
        user_id: str,
        role: str,
        type: str,
        title: str,
        message: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> dict:
        safe_data = normalize_value(data or {})

        doc = {
            "user_id": str(user_id),
            "role": str(role),
            "type": str(type),
            "title": str(title),
            "message": message,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": safe_data,
            "read_at": None,
            "created_at": dt.datetime.utcnow(),
        }

        res = self.col.insert_one(doc)
        doc["_id"] = res.inserted_id

        emit_notification(str(user_id), self._to_socket_payload(doc))
        return doc

    def _to_socket_payload(self, doc: dict) -> dict:
        return {
            "id": str(doc.get("_id")),
            "user_id": str(doc.get("user_id")),
            "role": str(doc.get("role")),
            "type": str(doc.get("type")),
            "title": str(doc.get("title")),
            "message": doc.get("message"),
            "entity_type": doc.get("entity_type"),
            "entity_id": doc.get("entity_id"),
            "data": normalize_value(doc.get("data") or {}),
            "read_at": _iso(doc.get("read_at")),
            "created_at": _iso(doc.get("created_at")),
        }