from typing import Optional, Sequence, Union
from datetime import datetime
from bson import ObjectId
from pymongo.database import Database

NotifTypeArg = Union[str, Sequence[str]]


class NotificationReadModel:
    def __init__(self, db: Database):
        self.col = db["notifications"]

    def list_latest(
        self,
        *,
        user_id: str,
        limit: int = 30,
        type: Optional[NotifTypeArg] = None,
        unread_only: bool = False,
    ) -> list[dict]:
        q: dict = {"user_id": str(user_id)}

        if unread_only:
            q["read_at"] = None

        if type:
            if isinstance(type, (list, tuple, set)):
                q["type"] = {"$in": [str(x) for x in type]}
            else:
                q["type"] = str(type)

        cur = self.col.find(q).sort("created_at", -1).limit(int(limit))
        return [self._to_dto(d) for d in cur]

    def count_unread(self, *, user_id: str, type: Optional[NotifTypeArg] = None) -> int:
        q: dict = {"user_id": str(user_id), "read_at": None}

        if type:
            if isinstance(type, (list, tuple, set)):
                q["type"] = {"$in": [str(x) for x in type]}
            else:
                q["type"] = str(type)

        return int(self.col.count_documents(q))

    def mark_read(self, *, user_id: str, notification_id: str) -> int:
        # small safety: if invalid ObjectId => 0 (instead of raising)
        try:
            oid = ObjectId(notification_id)
        except Exception:
            return 0

        res = self.col.update_one(
            {"_id": oid, "user_id": str(user_id), "read_at": None},
            {"$set": {"read_at": datetime.utcnow()}},
        )
        return int(res.modified_count)

    def mark_all_read(self, *, user_id: str, type: Optional[NotifTypeArg] = None) -> int:
        q: dict = {"user_id": str(user_id), "read_at": None}

        if type:
            if isinstance(type, (list, tuple, set)):
                q["type"] = {"$in": [str(x) for x in type]}
            else:
                q["type"] = str(type)

        res = self.col.update_many(q, {"$set": {"read_at": datetime.utcnow()}})
        return int(res.modified_count)

    def _iso(self, v):
        if v is None:
            return None
        try:
            return v.isoformat()
        except Exception:
            return str(v)

    def _to_dto(self, d: dict) -> dict:
        return {
            "id": str(d.get("_id")),
            "user_id": str(d.get("user_id")),
            "role": str(d.get("role")),
            "type": str(d.get("type")),
            "title": str(d.get("title")),
            "message": d.get("message"),
            "entity_type": d.get("entity_type"),
            "entity_id": d.get("entity_id"),
            "data": d.get("data") or {},
            "read_at": self._iso(d.get("read_at")),
            "created_at": self._iso(d.get("created_at")),
        }