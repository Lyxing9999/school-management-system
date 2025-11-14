
from app.contexts.shared.model_converter import mongo_converter
from pymongo.database import Database
from app.contexts.core.error import MongoErrorMixin
from bson import ObjectId
from pymongo import ASCENDING
class StaffReadModel(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "staff"):
        self.collection = db[collection_name]
        self.mongo_converter = mongo_converter


    def get_staff_by_id(self, staff_id: ObjectId) -> dict:
        try:
            cursor = self.collection.find_one({"user_id": staff_id})
            return cursor
        except Exception as e:
            self._handle_mongo_error("get_staff_by_id", e)
            return {}

    def get_staff_name_select(self, search_text: str = "", role: str = "teacher") -> list[dict]:
        """
        Return staff for select dropdown.
        Optional: search by partial staff_name.
        Returns list of dict: [{_id, user_id, staff_name}]
        """
        try:
            query = {}
            if search_text:
                # case-insensitive regex search
                query["staff_name"] = {"$regex": search_text, "$options": "i"}
            if role:
                query["role"] = role
            projection = {"_id": 1, "user_id": 1, "staff_name": 1}

            # Sort by staff_name ascending for nicer UX
            cursor = self.collection.find(query, projection).sort("staff_name", ASCENDING)
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error(e)



    # def get_staff_permissions(self, staff_id: ObjectId) -> dict:
    #     try:
    #         query = {"_id": staff_id, "deleted": False}
    #         projection = {"permissions": 1, "_id": 0}
    #         result = self.collection.find_one(query, projection)
    #         return result.get("permissions", {}) if result else {}
    #     except Exception as e:
    #         self._handle_mongo_error("get_employee_permissions", e)
    #         return {}

    # def get_staff_username_by_id(self, staff_id: ObjectId) -> str:
    #     try:
    #         cursor = self.collection.find_one({"_id": staff_id}, {"staff_name": 1})
    #         return cursor.get("staff_name") if cursor else ""
    #     except Exception as e:
    #         self._handle_mongo_error("get_staff_username_by_id", e)
    #         return ""


    # def get_staff_by_role_for_select(self, role: str) -> list[dict]:
    #     try:
    #         cursor = self.collection.find(
    #             {"role": role, "deleted": {"$ne": True}},
    #             {"staff_name": 1}
    #         )
    #         return list(cursor)
    #     except Exception as e:
    #         self._handle_mongo_error("get_staff_by_role_for_select", e)
    #         return []