from app.models.student import StudentModel # type: ignore
from typing import Optional, List, Dict, Any, Union
from app.utils.objectid import ObjectId # type: ignore
from pymongo.database import Database # type: ignore
from app.models.user import UserModel # type: ignore
from abc import ABC, abstractmethod
from app.error.exceptions import ExceptionFactory, AppBaseException, InternalServerError    
from app.utils.model_utils import default_model_utils


class StudentServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "student"

class StudentService(ABC):
    pass


class MongoStudentService(StudentService):
    def __init__(self, config: StudentServiceConfig):
        self.db = self.config.db
        self.collection = self.db[self.config.collection_name]
        self.utils = default_model_utils
        self._user_service = None
        self._classes_service = None

    @property
    def user_service(self):
        if self._user_service is None:
            from app.services.user_service import get_user_service
            self._user_service = get_user_service(self.db)
        return self._user_service
    @property
    def classes_service(self):
        if self._classes_service is None:
            from app.services.classes_service import get_classes_service
            self._classes_service = get_classes_service(self.db)
        return self._classes_service

    def create_student(self, data: Dict[str, Any]) -> Optional[UserModel]:
        return self.user_service.create_user(data)

    def get_student(self, _id: ObjectId | str) -> Optional[StudentModel]:
        return self.user_service.get_user(_id)

    def update_student(self, _id: ObjectId | str, data: Dict[str, Any]) -> Optional[StudentModel]:
        return self.user_service.update_user(_id, data)

    def delete_student(self, _id: ObjectId | str) -> bool:
        return self.user_service.delete_user(_id)
        






def get_student_service(db: Database) -> MongoStudentService:
    return MongoStudentService(StudentServiceConfig(db))