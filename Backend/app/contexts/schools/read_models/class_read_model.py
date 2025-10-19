
from pymongo.database import Database
from typing import List 
from bson.objectid import ObjectId
from app.contexts.core.log.log_service import LogService

from app.contexts.core.error import MongoErrorMixin
class ClassReadModel(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "classes"):
        self.collection = db[collection_name]
        self._log_service = LogService.get_instance()
    def _log(self, operation: str, class_id: str | None = None, extra: dict | None = None):
        msg = f"ClassReadModel::{operation}"
        if class_id:
            msg += f" [class_id={class_id}]"
        self._log_service.log(msg, level="INFO", module="ClassReadModel", extra=extra or {})
            
       
    def get_class(self) -> List[dict]:
        try:
            cursor = self.collection.find()
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("find", e)

        

    def find_by_id(self, class_id: ObjectId) -> dict | None:
        try:
            cursor = self.collection.find_one({"_id": class_id})
            return cursor
        except Exception as e:
            self._handle_mongo_error("find_one", e)
            