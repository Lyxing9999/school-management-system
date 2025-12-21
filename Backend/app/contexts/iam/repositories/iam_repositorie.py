from __future__ import annotations
from bson import ObjectId
from datetime import datetime

from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from pymongo.collection import Collection

from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.iam.domain.iam import IAM


class MongoIAMRepository(MongoErrorMixin):
    def __init__(self, collection: Collection):
        self.collection = collection
        self._iam_mapper = IAMMapper()
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
        user = dict(user)
        user.pop("_id", None)  # do not set _id
        self.collection.update_one({"_id": user_id}, {"$set": user})
        return self.find_one(user_id)

    #soft_delete & hard-delete will be handled by lifecycle service
    def hard_delete(self, user_id: ObjectId) -> None:
        self.collection.delete_one({"_id": user_id})

    def create_indexes(self):
        """Create necessary indexes for the collection."""
        self.collection.create_index([("email", 1)], unique=True, background=True)
        self.collection.create_index([("username", 1)], unique=True, background=True, sparse=True)