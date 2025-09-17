from pymongo.database import Database
from app.contexts.core.error import MongoErrorMixin
from app.contexts.staff.models import Staff
from bson import ObjectId

class StaffRepository(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "staff"):
        self.collection = db[collection_name]

    def save(self, staff: dict) -> ObjectId:
        try:
            return self.collection.insert_one(staff).inserted_id
        except Exception as e:
            raise self._handle_mongo_error("insert", e)


    def delete(self, staff_id: ObjectId) -> int:
        try:
            result = self.collection.delete_one({"_id": staff_id})
            return result.deleted_count
        except Exception as e:
            self._handle_mongo_error("delete", e)
    
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