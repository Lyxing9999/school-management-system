
from pymongo.database import Database
import logging
from app.contexts.schools.classes.models.school_class import SchoolClass
from typing import List , Any
logger = logging.getLogger(__name__)


from app.contexts.core.error import MongoErrorMixin
class ReadClassModel(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "classes"):
        self.collection = db[collection_name]

    def _log(self, operation: str, class_id: str | None = None, extra: dict | None = None):
        msg = f"ReadClassModel::{operation}"
        if class_id:
            msg += f" [class_id={class_id}]"
        logger.info(msg, extra=extra or {})
        
       
    def get_class(self) -> List[dict]:
        try:
            cursor = self.collection.find()
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("find", e)

        
