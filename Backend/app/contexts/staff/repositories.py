from datetime import datetime
from bson import ObjectId
from pymongo.database import Database
from app.contexts.core.error import MongoErrorMixin
from typing import Optional

from app.contexts.shared.model_converter import mongo_converter


class StaffRepository(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "staff"):
        self.collection = db[collection_name]

    # --- Save ---
    def save(self, staff: dict) -> ObjectId:
        try:
            return self.collection.insert_one(staff).inserted_id
        except Exception as e:
            raise self._handle_mongo_error("insert", e)

    # --- Delete ---
    def delete(self, staff_id: ObjectId) -> int:
        try:
            result = self.collection.delete_one({"_id": staff_id})
            return result.deleted_count
        except Exception as e:
            self._handle_mongo_error("delete", e)

    # --- Soft delete ---
    def soft_delete(self, staff_id: ObjectId, deleted_by: ObjectId | None = None) -> int:
        try:
            update_data = {
                "$set": {
                    "deleted": True,
                    "deleted_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
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

    # --- Update (partial/PATCH) ---
    def update(self, staff_id: ObjectId, payload: dict) -> int:
        """
        Partially update a staff document.
        Only fields present in `payload` will be updated.
        """
        if not payload:
            return 0  # Nothing to update
        oid = mongo_converter.convert_to_object_id(staff_id)
        # Add updated_at timestamp
        payload["updated_at"] = datetime.utcnow()

        try:
            result = self.collection.update_one(
                {"_id": oid, "deleted": {"$ne": True}},
                {"$set": payload}
            )
            return result.modified_count
        except Exception as e:
            self._handle_mongo_error("update", e)

    
    def exists_staff_id(self, staff_id: str, exclude_id: Optional[str] = None) -> bool:
        query = {"staff_id": staff_id}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        return self.collection.find_one(query) is not None


    def exists_staff_name(self, staff_name: str, exclude_id: Optional[str] = None) -> bool:
        query = {"staff_name": staff_name}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        return self.collection.find_one(query) is not None

    def exists_phone_number(self, phone_number: str, exclude_id: Optional[str] = None) -> bool:
        query = {"phone_number": phone_number}
        if exclude_id:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        return self.collection.find_one(query) is not None