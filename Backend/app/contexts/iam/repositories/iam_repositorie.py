from __future__ import annotations
from bson import ObjectId
from datetime import datetime
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.core.log.log_service import LogService

from pymongo.collection import Collection

from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.iam.domain.iam import IAM









class MongoIAMRepository(MongoErrorMixin):
    def __init__(self, collection: Collection):
        self.collection = collection
        self._iam_mapper = IAMMapper()
        self.logger = LogService.get_instance()
        self.create_indexes()



    def find_one(self, id: ObjectId) -> IAM | None:
        """Find a single user matching the query."""
        raw_user = self.collection.find_one({"_id": id})
        if not raw_user: return None
        return self._iam_mapper.to_domain(raw_user)


    def save(self, user_data: dict) -> IAM:
        """Insert a new user into the collection."""
        inserted_id = self.collection.insert_one(user_data).inserted_id
        iam = self.find_one(inserted_id)
        return iam


    def update(self, user_id: ObjectId, user: dict) -> IAM:
        """Update an existing user partially."""
        self.collection.update_one({"_id": user_id}, {"$set": user})
        iam = self.find_one(user_id)
        return iam


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


    def hard_delete(self, user_id: ObjectId) -> int:
        """Permanently delete a user from the collection."""
        result = self.collection.delete_one({"_id": user_id})
        return result.deleted_count


    def create_indexes(self):
        """Create necessary indexes for the collection."""
        self.collection.create_index(
            [("role", 1), ("email", 1)],
            unique=True,
            background=True
        )
