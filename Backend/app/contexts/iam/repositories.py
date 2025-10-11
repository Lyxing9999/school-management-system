from bson import ObjectId
from typing import Optional, List
from pymongo.database import Database
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from datetime import datetime
from app.contexts.core.log.log_service import LogService


class IAMRepository(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "users"):
        self.collection = db[collection_name]
        self.logger = LogService.get_instance()
        self.create_indexes()

    def create_indexes(self):
        try:
            self.collection.create_index([("role", 1), ("email", 1)], unique=True, background=True)
            self.logger.log("Indexes created for iam collection", level="INFO", module="IAMRepository")
        except Exception as e:
            self._handle_mongo_error("create_index", e)

    def find_one(self, query: dict) -> dict | None:
        try:
            result = self.collection.find_one(query)
            self.logger.log(
                f"find_one executed",
                level="INFO",
                module="iam",
                extra={"query": query, "found": bool(result)}
            )
            return result
        except Exception as e:
            self._handle_mongo_error("find_one", e)

    def save(self, user_data: dict) -> ObjectId:
        try:
            inserted_id = self.collection.insert_one(user_data).inserted_id
            self.logger.log(
                "User inserted",
                level="INFO",
                module="iam",
                extra={"user_id": str(inserted_id), "data": user_data}
            )
            return inserted_id
        except Exception as e:
            self._handle_mongo_error("save", e)

    def update(self, user_id: ObjectId, user: dict) -> None:
        try:
            result = self.collection.update_one({"_id": user_id}, {"$set": user})
            self.logger.log(
                "User updated",
                level="INFO",
                module="iam",
                extra={"user_id": str(user_id), "modified_count": result.modified_count, "data": user}
            )
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

            self.logger.log(
                "User soft-deleted",
                level="INFO",
                module="iam",
                extra={"user_id": str(staff_id), "modified_count": result.modified_count, "deleted_by": str(deleted_by)}
            )

            return result.modified_count
        except Exception as e:
            self._handle_mongo_error("soft_delete", e)

    def hard_delete(self, staff_id: ObjectId) -> int:
        try:
            result = self.collection.delete_one({"_id": staff_id})
            self.logger.log(
                "User hard-deleted",
                level="WARN",
                module="iam",
                extra={"user_id": str(staff_id), "deleted_count": result.deleted_count}
            )
            return result.deleted_count
        except Exception as e:
            self._handle_mongo_error("hard_delete", e)