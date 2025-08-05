from abc import ABC, abstractmethod
from pymongo.database import Database
from app.utils.pyobjectid import PyObjectId
from app.schemas.classes import ClassCreateSchema
from app.shared.model_utils import default_model_utils
from app.repositories.base_repo import get_base_repository, BaseRepositoryConfig
from typing import TypeVar, Generic, Type

R = TypeVar('R')  # Response DTO Type

class ClassService(ABC):

    @abstractmethod
    def create_class(self, class_data: ClassCreateSchema, model_response: Type[R]) -> R:
        pass
    

class ClassServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.class_collection = "classes"  # Plural for collection


class MongoClassService(ClassService, Generic[R]):
    def __init__(self, config: ClassServiceConfig):
        self.config = config
        self.db = config.db
        self.collection = self.db[self.config.class_collection]
        repo_config = BaseRepositoryConfig(db=self.db, collection_name=self.config.class_collection)
        self._base_repo = get_base_repository(repo_config)
        self.utils = default_model_utils

    def create_class(self, class_data: ClassCreateSchema, model_response: Type[R]) -> R:
        data = class_data.model_dump(by_alias=True)
        insert_result = self._base_repo.insert_one(data)
        insert_doc = self._base_repo.find_by_query({"_id": insert_result})
        class_dto = self.utils.convert_to_response_model_dto(insert_doc, model_response)
        return class_dto