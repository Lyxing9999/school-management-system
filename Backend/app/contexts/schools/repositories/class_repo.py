# app/contexts/school/classes/repositories.py
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime
from typing import Any, Dict
from app.contexts.core.error import MongoErrorMixin
from app.contexts.schools.models.school_class import SchoolClass
from app.contexts.core.log.log_service import LogService

class ClassRepository(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "classes"):
        self.collection = db[collection_name]
        self._log_service = LogService.get_instance()


    def _log(self, operation: str, class_id: str | None = None, extra: dict | None = None):
        msg = f"ClassRepository::{operation}"
        if class_id:
            msg += f" [class_id={class_id}]"
        self._log_service.log(msg, level="INFO", module="ClassRepository", extra=extra or {}) 

    def _update_field(self, class_id: ObjectId, update_data: Dict[str, Any]) -> int:
        try:
            result = self.collection.update_one({"_id": class_id, "deleted": {"$ne": True}}, update_data)
            return result.modified_count
        except Exception as e:
            self._handle_mongo_error("update", e)

    def save(self, class_agg: SchoolClass) -> ObjectId:
        try:
            result = self.collection.insert_one(class_agg)
            self._log("save", f"Class ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            self._handle_mongo_error("insert", e)

    def update(self, class_id: ObjectId, update_query: Dict[str, Any]) -> int:
        return self._update_field(class_id, update_query)

    def soft_delete(self, class_id: ObjectId) -> int:
        return self._update_field(class_id, {
            "$set": {"deleted": True, "deleted_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
        })

    def add_to_set(self, class_id: ObjectId, field: str, values: list | Any) -> int:
        if isinstance(values, list):
            update = {"$addToSet": {field: {"$each": values}}, "$set": {"updated_at": datetime.utcnow()}}
        else:
            update = {"$addToSet": {field: values}, "$set": {"updated_at": datetime.utcnow()}}
        return self._update_field(class_id, update)

    def pull_from_set(self, class_id: ObjectId, field: str, values: list | Any) -> int:
        if isinstance(values, list):
            update = {"$pullAll": {field: values}, "$set": {"updated_at": datetime.utcnow()}}
        else:
            update = {"$pull": {field: values}, "$set": {"updated_at": datetime.utcnow()}}
        return self._update_field(class_id, update)

    def patch(self, class_id: ObjectId, partial_fields: Dict[str, Any]) -> int:
        return self._update_field(class_id, {"$set": {**partial_fields, "updated_at": datetime.utcnow()}})