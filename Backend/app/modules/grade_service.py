from app.models.grade import GradeModel
from app.error.exceptions import NotFoundError, ValidationError, DatabaseError, ExceptionFactory, InternalServerError, AppBaseException, BadRequestError, ErrorSeverity , ErrorCategory
from app.utils.objectid import ObjectId
from typing import Optional, Dict, Any, Union
from app.services.base.base_utils_service import BaseServiceUtils
from abc import ABC, abstractmethod
from pymongo.database import Database

class GradeServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "grade"


class GradeService(ABC):
    @abstractmethod
    def create_grade(self, data: Dict[str, Any]) -> Optional[GradeModel]:
        pass

class MongoGradeService(GradeService):
    def __init__(self, config: GradeServiceConfig):
        self.config = config
        self.db = config.db
        self.collection = self.db[self.config.collection_name]
        self.utils = BaseServiceUtils(self.db, GradeModel)

    def create_grade(self, data: Dict[str, Any]) -> Optional[GradeModel]:
        grade = self.utils._to_model(data)
        try:
            result = self.collection.insert_one(grade.model_dump(by_alias=True, exclude_none=True, mode="json"))
            return self.utils._fetch_first_inserted(result.inserted_id)
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while creating grade", cause=e)






def get_grade_service(db: Database) -> MongoGradeService:
    return MongoGradeService(GradeServiceConfig(db))

