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
    def get_by_id(self, id: ObjectId) -> Optional[Dict]:
        try:
            doc = self.collection.find_one(
                {"_id": id, "deleted": {"$ne": True}}
            )
            return doc
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)
            return None
    
    def get_name_by_id(self, id: ObjectId) -> str:
        try:
            doc = self.collection.find_one(
                {"_id": id, "deleted": {"$ne": True}},
                {"staff_name": 1},
            )
            return doc.get("staff_name", "") if doc else ""
        except Exception as e:
            self._handle_mongo_error("get_name_by_id", e)
            return ""

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

    def list_by_ids(self, ids: List[ObjectId]) -> List[Dict]:
        """
        Fetch all staff documents for the given user_ids (ignores soft-deleted records).
        """
        if not ids:
            return []
        try:
            cursor = self.collection.find(
                {"_id": {"$in": ids}, "deleted": {"$ne": True}}
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_by_ids", e)
            return []



    def list_names_by_ids(self, ids: List[ObjectId]) -> Dict[ObjectId, str]:
        """
        Given a list of ids, return a mapping {id: staff_name}.
        Only returns entries for staff that exist and are not deleted.
        """
        if not ids:
            return {}
        try:
            cursor = self.collection.find(
                {"_id": {"$in": ids}, "deleted": {"$ne": True}},
                {"staff_name": 1},
            )
            result: Dict[ObjectId, str] = {}
            for doc in cursor:
                id = doc.get("_id")
                name = doc.get("staff_name")
                if id is not None and name is not None:
                    result[id] = name
            return result
        except Exception as e:
            self._handle_mongo_error("list_names_by_ids", e)
            return {}

    def list_names_by_user_ids(self, ids: List[ObjectId]) -> Dict[ObjectId, str]:
        """
        Given a list of ids, return a mapping {id: staff_name}.
        Only returns entries for staff that exist and are not deleted.
        """
        if not ids:
            return {}
        try:
            cursor = self.collection.find(
                {"user_id": {"$in": ids}, "deleted": {"$ne": True}},
                {"_id": 0, "user_id": 1, "staff_name": 1},
            )
            result: Dict[ObjectId, str] = {}
            for doc in cursor:
                id = doc.get("user_id")
                name = doc.get("staff_name")
                if id is not None and name is not None:
                    result[id] = name
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
        Return [{_id, staff_name}, ...] for given role, for select/dropdown usage.
        Ignores soft-deleted records.
        """
        try:
            cursor = self.collection.find(
                {"role": role, "deleted": False},
                {"_id": 1, "staff_name": 1},
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_staff_name_options", e)
            return []




            
    def count_active_teachers(self) -> int:
        """
        Return the count of active teachers.
        """
        return self.collection.count_documents({"role": "teacher", "deleted": False})