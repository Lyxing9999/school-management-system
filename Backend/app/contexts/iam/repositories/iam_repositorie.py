from typing import Optional

from bson import ObjectId
from pymongo.collection import Collection

from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.iam.domain.iam import IAM
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.shared.lifecycle.filters import not_deleted, by_show_deleted
from app.contexts.shared.lifecycle.domain import now_utc as lifecycle_now_utc


class MongoIAMRepository(MongoErrorMixin):
    def __init__(self, collection: Collection):
        self.collection = collection
        self._iam_mapper = IAMMapper()

    def find_one(self, id: ObjectId, *, include_deleted: bool = False) -> Optional[IAM]:
        show = "all" if include_deleted else "active"
        raw_user = self.collection.find_one(by_show_deleted(show, {"_id": id}))
        return None if not raw_user else self._iam_mapper.to_domain(raw_user)

    def save(self, user_data: dict) -> IAM:
        payload = dict(user_data)
        res = self.collection.insert_one(payload)
        iam = self.find_one(res.inserted_id)
        if iam is None:
            raise RuntimeError(f"IAM insert succeeded but could not load user: {res.inserted_id}")
        return iam

    def update(self, user_id: ObjectId, user: dict) -> Optional[IAM]:
        payload = dict(user)
        payload.pop("_id", None)

        # Important: don't replace entire lifecycle dict unless you explicitly want to.
        payload.pop("lifecycle", None)

        res = self.collection.update_one(
            not_deleted({"_id": user_id}),
            {
                "$set": {
                    **payload,
                    "lifecycle.updated_at": lifecycle_now_utc(),
                }
            },
        )
        if res.matched_count == 0:
            return None

        return self.find_one(user_id)

    def update_password(self, user_id: ObjectId | str, password_hash: str) -> int:
        oid = ObjectId(user_id) if isinstance(user_id, str) else user_id

        res = self.collection.update_one(
            not_deleted({"_id": oid}),
            {
                "$set": {
                    "password": password_hash,
                    "lifecycle.updated_at": lifecycle_now_utc(),
                }
            },
        )
        return int(res.modified_count)

    def hard_delete(self, user_id: ObjectId) -> None:
        self.collection.delete_one({"_id": user_id})