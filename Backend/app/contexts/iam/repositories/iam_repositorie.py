from bson import ObjectId
from pymongo.database import Database
from datetime import datetime
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.core.log.log_service import LogService
from app.contexts.shared.decorators.mongo_wrappers import mongo_operation


class IAMRepository(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "users"):
        self.collection = db[collection_name]
        self.logger = LogService.get_instance()
        self.create_indexes()

    @mongo_operation("find_one")
    def find_one(self, query: dict) -> dict | None:
        """Find a single user matching the query."""
        return self.collection.find_one(query)

    @mongo_operation("insert")
    def save(self, user_data: dict) -> ObjectId:
        """Insert a new user into the collection."""
        return self.collection.insert_one(user_data).inserted_id

    @mongo_operation("update")
    def update(self, user_id: ObjectId, user: dict) -> int:
        """Update an existing user partially."""
        result = self.collection.update_one({"_id": user_id}, {"$set": user})
        return result.modified_count

    @mongo_operation("soft_delete")
    def soft_delete(self, user_id: ObjectId, deleted_by: ObjectId | None = None) -> int:
        """Soft delete a user by marking it as deleted."""
        update_data = {"$set": { "deleted": True, "deleted_at": datetime.utcnow(),"updated_at": datetime.utcnow(),}}
        if deleted_by:
            update_data["$set"]["deleted_by"] = deleted_by

        result = self.collection.update_one(
            {"_id": user_id, "deleted": {"$ne": True}},
            update_data
        )
        return result.modified_count

    @mongo_operation("hard_delete")
    def hard_delete(self, user_id: ObjectId) -> int:
        """Permanently delete a user from the collection."""
        result = self.collection.delete_one({"_id": user_id})
        return result.deleted_count

    
    def create_indexes(self):
        """Create necessary indexes for the collection."""
        try:
            self.collection.create_index(
                [("role", 1), ("email", 1)],
                unique=True,
                background=True
            )
            self.logger.log(
                "Indexes created for iam collection",
                level="INFO",
                module="IAMRepository"
            )
        except Exception as e:
            self._handle_mongo_error("create_index", e)
