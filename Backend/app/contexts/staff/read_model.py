
from pymongo.database import Database
from app.contexts.core.error import MongoErrorMixin
from bson import ObjectId
class StaffReadModel(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "staff"):
        self.collection = db[collection_name]


    def get_staff_by_id(self, staff_id: ObjectId) -> dict:
        try:
            cursor = self.collection.find_one({"user_id": staff_id})
            return cursor
        except Exception as e:
            self._handle_mongo_error("get_staff_by_id", e)
            return {}

    def list_by_user_ids(self, user_ids: list[ObjectId]) -> list[dict]:
        if not user_ids:
            return []
        cursor = self.collection.find({"user_id": {"$in": user_ids}})
        return list(cursor)
    def get_staff_name_select(self, role: str = "teacher") -> list[dict]:
        try:
            cursor = self.collection.find({"role": role, "deleted": False}, {"user_id": 1, "staff_name": 1})
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("get_staff_name_select", e)



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