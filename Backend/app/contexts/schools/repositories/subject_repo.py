from app.contexts.core.error import MongoErrorMixin
from app.contexts.schools.models.subject import SchoolSubject
from app.contexts.core.log.log_service import LogService
from bson import ObjectId
from pymongo.database import Database




class SubjectRepository(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "subjects"):
        self.collection = db[collection_name]

    def save(self, subject_agg: SchoolSubject) -> ObjectId:
        try:
            result = self.collection.insert_one(subject_agg)
            self._log("save", f"Subject ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            self._handle_mongo_error("insert", e)