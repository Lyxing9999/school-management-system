from bson import ObjectId
from typing import Optional, List
from pymongo.database import Database
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.iam.models import User
from datetime import datetime
class UserRepository(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "users"):
        self.collection = db[collection_name]

    def save(self, user_data: dict) -> ObjectId:
        try:    
            return self.collection.insert_one(user_data).inserted_id
        except Exception as e:
            self._handle_mongo_error("insert", e)

    def update(self, user_id: ObjectId, user: User) -> None:
        try:
            self.collection.update_one({"_id": user_id}, {"$set": user})
        except Exception as e:
            self._handle_mongo_error("update", e)

    def soft_delete(self, staff_id: ObjectId, deleted_by: ObjectId | None = None) -> int:
        try:
            update_data = {
                "$set": {
                    "deleted": True,
                    "deleted_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
            if deleted_by:
                update_data["$set"]["deleted_by"] = deleted_by

            result = self.collection.update_one(
                {"_id": staff_id, "deleted": {"$ne": True}},
                update_data
            )
            return result.modified_count
        except Exception as e:
            self._handle_mongo_error("soft_delete", e)

    def hard_delete(self, staff_id: ObjectId) -> int:
        try:
            result = self.collection.delete_one({"_id": staff_id}) 
            return result.deleted_count
        except Exception as e:
            self._handle_mongo_error("hard_delete", e)