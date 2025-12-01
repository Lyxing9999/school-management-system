from typing import Optional, List, Dict
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection

from app.contexts.core.error import MongoErrorMixin


class StaffReadModel(MongoErrorMixin):
    """
    Read-side helper for staff data.

    Returned objects are plain dicts (Mongo docs), not domain aggregates.
    """

    def __init__(self, db: Database, collection_name: str = "staff"):
        self.collection: Collection = db[collection_name]

    # ------------ core getters ------------

    def get_by_user_id(self, user_id: ObjectId) -> Optional[Dict]:
        """
        Fetch staff document by user_id (ignores soft-deleted records).
        """
        try:
            doc = self.collection.find_one(
                {"user_id": user_id, "deleted": {"$ne": True}}
            )
            return doc
        except Exception as e:
            self._handle_mongo_error("get_by_user_id", e)
            return None

    def get_name_by_user_id(self, user_id: ObjectId) -> str:
        """
        Fetch staff_name by user_id (ignores soft-deleted records).
        Returns empty string if not found or on error.
        """
        try:
            doc = self.collection.find_one(
                {"user_id": user_id, "deleted": {"$ne": True}},
                {"staff_name": 1},
            )
            return doc.get("staff_name", "") if doc else ""
        except Exception as e:
            self._handle_mongo_error("get_name_by_user_id", e)
            return ""

    # ------------ list / batch APIs ------------

    def list_by_user_ids(self, user_ids: List[ObjectId]) -> List[Dict]:
        """
        Fetch all staff documents for the given user_ids (ignores soft-deleted records).
        """
        if not user_ids:
            return []
        try:
            cursor = self.collection.find(
                {"user_id": {"$in": user_ids}, "deleted": {"$ne": True}}
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_by_user_ids", e)
            return []

    def list_names_by_user_ids(self, user_ids: List[ObjectId]) -> Dict[ObjectId, str]:
        """
        Given a list of user_ids, return a mapping {user_id: staff_name}.
        Only returns entries for staff that exist and are not deleted.
        """
        if not user_ids:
            return {}
        try:
            cursor = self.collection.find(
                {"user_id": {"$in": user_ids}, "deleted": {"$ne": True}},
                {"_id": 0, "user_id": 1, "staff_name": 1},
            )
            result: Dict[ObjectId, str] = {}
            for doc in cursor:
                uid = doc.get("user_id")
                name = doc.get("staff_name")
                if uid is not None and name is not None:
                    result[uid] = name
            return result
        except Exception as e:
            self._handle_mongo_error("list_names_by_user_ids", e)
            return {}

    # ------------ select helpers (for dropdowns, etc.) ------------

    def list_staff_name_options(
        self,
        role: str = "teacher",
    ) -> List[Dict]:
        """
        Return [{user_id, staff_name}, ...] for given role, for select/dropdown usage.
        Ignores soft-deleted records.
        """
        try:
            cursor = self.collection.find(
                {"role": role, "deleted": False},
                {"user_id": 1, "staff_name": 1},
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_staff_name_options", e)
            return []




            