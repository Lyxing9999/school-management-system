from __future__ import annotations

from typing import Optional, List, Dict, Any
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.error import MongoErrorMixin
from app.contexts.shared.lifecycle.filters import not_deleted, by_show_deleted
from app.contexts.shared.decorators.mongo_wrappers import mongo_operation


class StaffReadModel(MongoErrorMixin):
    """
    Read-side helper for staff data.

    Returns Mongo docs (dict), not domain entities.
    Default behavior excludes soft-deleted records using lifecycle.deleted_at.
    """

    def __init__(self, db: Database):
        self.collection = db.staff

    # ------------ core getters ------------

    @mongo_operation("get_by_user_id")
    def get_by_user_id(self, user_id: ObjectId, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        q = {"user_id": user_id} if include_deleted else not_deleted({"user_id": user_id})
        return self.collection.find_one(q)

    @mongo_operation("get_by_id")
    def get_by_id(self, id: ObjectId, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        q = {"_id": id} if include_deleted else not_deleted({"_id": id})
        return self.collection.find_one(q)

    @mongo_operation("get_name_by_id")
    def get_name_by_id(self, id: ObjectId, include_deleted: bool = False) -> str:
        q = {"_id": id} if include_deleted else not_deleted({"_id": id})
        doc = self.collection.find_one(q, {"staff_name": 1})
        return doc.get("staff_name", "") if doc else ""

    @mongo_operation("get_name_by_user_id")
    def get_name_by_user_id(self, user_id: ObjectId, include_deleted: bool = False) -> str:
        q = {"user_id": user_id} if include_deleted else not_deleted({"user_id": user_id})
        doc = self.collection.find_one(q, {"staff_name": 1})
        return doc.get("staff_name", "") if doc else ""

    # ------------ list / batch APIs ------------

    @mongo_operation("list_by_ids")
    def list_by_ids(self, ids: List[ObjectId], include_deleted: bool = False) -> List[Dict[str, Any]]:
        if not ids:
            return []
        base = {"_id": {"$in": ids}}
        q = base if include_deleted else not_deleted(base)
        return list(self.collection.find(q))

    @mongo_operation("list_names_by_ids")
    def list_names_by_ids(self, ids: List[ObjectId], include_deleted: bool = False) -> Dict[ObjectId, str]:
        if not ids:
            return {}
        base = {"_id": {"$in": ids}}
        q = base if include_deleted else not_deleted(base)

        cursor = self.collection.find(q, {"staff_name": 1})
        result: Dict[ObjectId, str] = {}
        for doc in cursor:
            _id = doc.get("_id")
            name = doc.get("staff_name")
            if _id is not None and name is not None:
                result[_id] = name
        return result

    @mongo_operation("list_names_by_user_ids")
    def list_names_by_user_ids(self, user_ids: List[ObjectId], include_deleted: bool = False) -> Dict[ObjectId, str]:
        if not user_ids:
            return {}
        base = {"user_id": {"$in": user_ids}}
        q = base if include_deleted else not_deleted(base)

        cursor = self.collection.find(q, {"_id": 0, "user_id": 1, "staff_name": 1})
        result: Dict[ObjectId, str] = {}
        for doc in cursor:
            uid = doc.get("user_id")
            name = doc.get("staff_name")
            if uid is not None and name is not None:
                result[uid] = name
        return result

    # ------------ list for UI (dropdown/select) ------------
    @mongo_operation("list_staff_name_options")
    def list_staff_name_options(
        self,
        role: str = "teacher",
        show_deleted: str = "active",
    ) -> List[Dict[str, Any]]:
        q = by_show_deleted(show_deleted, {"role": role})

        cursor = self.collection.find(q, {"_id": 1, "staff_name": 1, "username": 1}).sort("staff_name", 1)

        items: List[Dict[str, Any]] = []
        for doc in cursor:
            label = (doc.get("staff_name") or doc.get("username") or "").strip()
            if not label:
                continue

            items.append({
                "value": str(doc["_id"]),  # IMPORTANT: ObjectId -> str
                "label": label,
            })

        return items
    # ------------ stats ------------

    @mongo_operation("count_active_teachers")
    def count_active_teachers(self) -> int:
        q = not_deleted({"role": "teacher"})
        return self.collection.count_documents(q)

    # ------------ general list ------------

    @mongo_operation("get_all_staff")
    def get_all_staff(self, show_deleted: str = "active") -> List[Dict[str, Any]]:
        """
        show_deleted: "active" | "deleted" | "all"
        """
        q = by_show_deleted(show_deleted)
        return list(self.collection.find(q))