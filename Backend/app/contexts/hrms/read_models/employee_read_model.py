from __future__ import annotations

from typing import Any, Dict, List, Tuple

from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import ShowDeleted, by_show_deleted
from app.contexts.shared.model_converter import mongo_converter


class EmployeeReadModel:
    def __init__(self, db: Database):
        self.collection = db["hr_employees"]

    @staticmethod
    def _oid(value) -> ObjectId | None:
        return mongo_converter.convert_to_object_id(value)

    def get_by_id(
        self,
        employee_id: ObjectId | str,
        *,
        show_deleted: str = "active",
    ) -> dict | None:
        oid = self._oid(employee_id)
        if not oid:
            return None

        return self.collection.find_one(
            by_show_deleted(show_deleted, {"_id": oid})
        )

    def get_by_employee_code(
        self,
        employee_code: str,
        *,
        show_deleted: str = "active",
    ) -> dict | None:
        code = (employee_code or "").strip()
        if not code:
            return None

        return self.collection.find_one(
            by_show_deleted(show_deleted, {"employee_code": code})
        )

    def find_by_user_id(
        self,
        user_id: ObjectId | str,
        *,
        show_deleted: str = "active",
    ) -> dict | None:
        oid = self._oid(user_id)
        if not oid:
            return None

        return self.collection.find_one(
            by_show_deleted(show_deleted, {"user_id": oid})
        )

    def get_page(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        q: str | None = None,
        show_deleted: str = "active",
    ) -> Tuple[List[dict], int]:
        page = max(1, int(page))
        page_size = min(max(1, int(page_size)), 100)
        skip = (page - 1) * page_size

        base: Dict[str, Any] = {}

        if q and (search := q.strip()):
            base["$or"] = [
                {"employee_code": {"$regex": search, "$options": "i"}},
                {"full_name": {"$regex": search, "$options": "i"}},
                {"department": {"$regex": search, "$options": "i"}},
                {"position": {"$regex": search, "$options": "i"}},
            ]

        query = by_show_deleted(show_deleted, base)
        total = self.collection.count_documents(query)

        items = list(
            self.collection.find(query)
            .sort("lifecycle.created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        return items, total

    def list_team_by_manager_user_id(
        self,
        *,
        manager_user_id,
        show_deleted: str = "active",
    ) -> list[dict]:
        manager_oid = self._oid(manager_user_id)
        if not manager_oid:
            return []

        query = by_show_deleted(
            show_deleted,
            {
                "manager_user_id": manager_oid,
            },
        )

        return list(
            self.collection.find(query).sort("full_name", 1)
        )