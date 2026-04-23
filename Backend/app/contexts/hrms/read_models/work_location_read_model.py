# app/contexts/hrms/read_models/work_location_read_model.py
from typing import Tuple, List, Dict, Any
from bson import ObjectId
from pymongo.database import Database
from app.contexts.shared.lifecycle.filters import by_show_deleted, ShowDeleted
from app.contexts.shared.model_converter import mongo_converter


class WorkLocationReadModel:
    def __init__(self, db: Database):
        self.collection = db["hr_work_locations"]

    def get_by_id(self, location_id: ObjectId | str, *, show_deleted: ShowDeleted = "active") -> dict | None:
        oid = mongo_converter.convert_to_object_id(location_id)
        if not oid:
            return None
        return self.collection.find_one(by_show_deleted(show_deleted, {"_id": oid}))

    def get_by_name(self, name: str, *, show_deleted: ShowDeleted = "active") -> dict | None:
        name_clean = (name or "").strip()
        if not name_clean:
            return None
        return self.collection.find_one(by_show_deleted(show_deleted, {"name": name_clean}))

    def get_active_locations(self) -> List[dict]:
        """Get all active work locations"""
        return list(self.collection.find(by_show_deleted("active", {"is_active": True})))

    def get_page(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        q: str | None = None,
        is_active: bool | None = None,
        show_deleted: ShowDeleted = "active",
    ) -> Tuple[List[Dict[str, Any]], int]:
        page = max(1, int(page))
        page_size = min(max(1, int(page_size)), 100)
        skip = (page - 1) * page_size

        base: Dict[str, Any] = {}
        
        if q and (s := q.strip()):
            base["$or"] = [
                {"name": {"$regex": s, "$options": "i"}},
                {"address": {"$regex": s, "$options": "i"}},
            ]
        
        if is_active is not None:
            base["is_active"] = is_active

        query = by_show_deleted(show_deleted, base)
        total = self.collection.count_documents(query)

        items = list(
            self.collection.find(query)
            .sort("lifecycle.created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        return items, total

    def list_by_ids(
        self,
        ids: List[ObjectId | str],
        *,
        show_deleted: ShowDeleted = "active",
    ) -> List[dict]:
        oids = [mongo_converter.convert_to_object_id(item) for item in ids]
        oids = [oid for oid in oids if oid is not None]
        if not oids:
            return []

        query = by_show_deleted(show_deleted, {"_id": {"$in": oids}})
        return list(self.collection.find(query))
