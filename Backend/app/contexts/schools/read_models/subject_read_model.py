


from pymongo.database import Database
from typing import List 
from bson.objectid import ObjectId
from app.contexts.core.log.log_service import LogService

from app.contexts.core.error import MongoErrorMixin
class SubjectReadModel(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "subjects"):
        self.collection = db[collection_name]
        self._log_service = LogService.get_instance()
    def _log(self, operation: str, subject_id: str | None = None, extra: dict | None = None):
        msg = f"SubjectReadModel::{operation}"
        if subject_id:
            msg += f" [subject_id={subject_id}]"
        self._log_service.log(msg, level="INFO", module="SubjectReadModel", extra=extra or {})
            
       
    def get_subject(self) -> List[dict]:
        try:
            cursor = self.collection.find()
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("find", e)

        

    def find_by_id(self, subject_id: ObjectId) -> dict | None:
        try:
            cursor = self.collection.find_one({"_id": subject_id})
            return cursor
        except Exception as e:
            self._handle_mongo_error("find_one", e)