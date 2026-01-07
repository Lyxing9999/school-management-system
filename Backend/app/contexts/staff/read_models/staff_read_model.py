from typing import Any, Dict, List, Optional, Iterable
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.shared.decorators.mongo_wrappers import mongo_operation
from app.contexts.shared.lifecycle.filters import by_show_deleted, not_deleted
from app.contexts.shared.lifecycle.filters import ShowDeleted


class StaffReadModel(MongoErrorMixin):
    def __init__(self, db: Database):
        self.collection: Collection = db["staff"]

    @mongo_operation("get_by_user_id")
    def get_by_user_id(
        self,
        user_id: ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        q = by_show_deleted(show_deleted, {"user_id": user_id})
        return self.collection.find_one(q)

    @mongo_operation("get_by_id")
    def get_by_id(
        self,
        id: ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Optional[Dict[str, Any]]:
        q = by_show_deleted(show_deleted, {"_id": id})
        return self.collection.find_one(q)

    @mongo_operation("get_name_by_id")
    def get_name_by_id(
        self,
        id: ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> str:
        q = by_show_deleted(show_deleted, {"_id": id})
        doc = self.collection.find_one(q, {"staff_name": 1})
        return (doc.get("staff_name") or "") if doc else ""

    @mongo_operation("get_name_by_user_id")
    def get_name_by_user_id(
        self,
        user_id: ObjectId,
        *,
        show_deleted: ShowDeleted = "active",
    ) -> str:
        q = by_show_deleted(show_deleted, {"user_id": user_id})
        doc = self.collection.find_one(q, {"staff_name": 1})
        return (doc.get("staff_name") or "") if doc else ""

    @mongo_operation("list_by_ids")
    def list_by_ids(
        self,
        ids: List[ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[Dict[str, Any]]:
        if not ids:
            return []
        q = by_show_deleted(show_deleted, {"_id": {"$in": ids}})
        return list(self.collection.find(q))

    @mongo_operation("list_names_by_ids")
    def list_names_by_ids(
        self,
        ids: List[ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[ObjectId, str]:
        if not ids:
            return {}
        q = by_show_deleted(show_deleted, {"_id": {"$in": ids}})
        cursor = self.collection.find(q, {"staff_name": 1})

        result: Dict[ObjectId, str] = {}
        for doc in cursor:
            _id = doc.get("_id")
            name = doc.get("staff_name")
            if _id is not None and name:
                result[_id] = str(name)
        return result

    @mongo_operation("list_names_by_user_ids")
    def list_names_by_user_ids(
        self,
        user_ids: List[ObjectId],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> Dict[ObjectId, str]:
        if not user_ids:
            return {}
        q = by_show_deleted(show_deleted, {"user_id": {"$in": user_ids}})
        cursor = self.collection.find(q, {"_id": 0, "user_id": 1, "staff_name": 1})

        result: Dict[ObjectId, str] = {}
        for doc in cursor:
            uid = doc.get("user_id")
            name = doc.get("staff_name")
            if uid is not None and name:
                result[uid] = str(name)
        return result
    @mongo_operation("list_staff_name_options")
    def list_staff_name_options(
        self,
        role: str = "teacher",
        show_deleted: ShowDeleted = "active",
        *,
        active_user_ids: Optional[Iterable[ObjectId]] = None,
    ) -> List[Dict[str, Any]]:
        base = {"role": role}

        if active_user_ids is not None:
            ids = list(active_user_ids)
            if not ids:
                return []
            base["user_id"] = {"$in": ids}

        q = by_show_deleted(show_deleted, base)

        cursor = (
            self.collection.find(q, {"_id": 1, "staff_name": 1, "username": 1})
            .sort("staff_name", 1)
        )

        items: List[Dict[str, Any]] = []
        for doc in cursor:
            label = (doc.get("staff_name") or doc.get("username") or "").strip()
            _id = doc.get("_id")
            if not label or not _id:
                continue
            items.append({"value": str(_id), "label": label})
        return items
    @mongo_operation("count_active_teachers")
    def count_active_teachers(self) -> int:
        return int(self.collection.count_documents(not_deleted({"role": "teacher"})))

    @mongo_operation("get_all_staff")
    def get_all_staff(self, show_deleted: ShowDeleted = "active") -> List[Dict[str, Any]]:
        q = by_show_deleted(show_deleted)
        return list(self.collection.find(q))