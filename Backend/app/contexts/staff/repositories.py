from pymongo.database import Database
from app.contexts.core.error import MongoErrorMixin
from app.contexts.staff.models import Staff
from bson import ObjectId

class StaffRepository(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "staff"):
        self.collection = db[collection_name]

    def save(self, staff: dict) -> ObjectId:
        """
        Inserts a new staff document. Raises a friendly error if duplicate exists.
        """
        try:
            return self.collection.insert_one(staff).inserted_id
        except Exception as e:
            raise self._handle_mongo_error("insert", e)

    def delete(self, staff_id: ObjectId) -> None:
        try:
            self.collection.delete_one({"_id": staff_id})
        except Exception as e:
            raise self._handle_mongo_error("delete", e)