from abc import ABC, abstractmethod
from pymongo.database import Database
from app.utils.pyobjectid import PyObjectId
from app.schemas.classes import ClassCreateSchema, ClassUpdateSchema
from app.shared.model_utils import default_model_utils
from app.repositories.base_repo import get_base_repository, BaseRepositoryConfig
from typing import TypeVar, Generic, Type, Dict
from pymongo.collection import Collection as MongoCollection

T = TypeVar('T')  # Request Schema Type
R = TypeVar('R')  # Response DTO Type

class ClassService(ABC):

    @abstractmethod
    def create_class(self, class_data: Type[T], model_response: Type[R], projection: Dict[str, int] | None = None, collection: MongoCollection | None = None) -> R:
        pass
    

class ClassServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.classes_collection_name = "classes"

class MongoClassService(ClassService, Generic[T, R]):
    def __init__(self, config: ClassServiceConfig):
        self.config = config
        repo_config = BaseRepositoryConfig(db=config.db, collection_name=config.classes_collection_name)
        self._base_repo = get_base_repository(repo_config)
        self.utils = default_model_utils

    def create_class( self, class_data: T, model_response: Type[R], projection: Dict[str, int] | None = None, collection: MongoCollection | None = None) -> R:
        if collection is None:
            collection = self._base_repo.collection     
        
        insert_doc = self._base_repo.insert_with_fetch(
            document=class_data,    
            projection=projection,
            collection=collection
        )
        class_dto = self.utils.convert_to_response_model_dto(insert_doc, model_response)
        return class_dto
        

    def update_class(self, class_id: PyObjectId, class_data: Type[T] , model_response: Type[R]) -> R:
        data = class_data.model_dump(by_alias=True)
        update_doc = self._base_repo.update_with_fetch({"_id": class_id}, data)
        class_dto = self.utils.convert_to_response_model_dto(update_doc, model_response)
        return class_dto




def get_class_service(db: Database) -> ClassService:
    return MongoClassService(ClassServiceConfig(db))