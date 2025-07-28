from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pymongo.database import Database, Collection
from app.error.exceptions import InternalServerError, ErrorSeverity, ErrorCategory
from app.shared.model_utils import default_model_utils


class BaseRepositoryConfig:
    def __init__(self, db: Database, collection_name: str):
        self.db = db
        self.collection_name = collection_name



class BaseRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def find_by_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def insert_one(self, data: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def update_one(self, query: Dict[str, Any], data: Dict[str, Any]) -> int:
        pass

    @abstractmethod
    def delete_one(self, query: Dict[str, Any]) -> int:
        pass


class MongoBaseRepository(BaseRepository):
    def __init__(self, config: BaseRepositoryConfig):
        self.config = config
        self.collection = self.config.db[self.config.collection_name]
        self.utils = default_model_utils

    def find_all(self) -> List[Dict[str, Any]]:
        try:
            return list(self.collection.find())
        except Exception as e:
            raise InternalServerError(
                message=f"Error fetching all documents from {self.config.collection_name} collection: {str(e)}",
                cause=e,
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
            )

    def find_by_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.collection.find_one(query)
        except Exception as e:
            raise InternalServerError(
                message=f"Error fetching document from {self.config.collection_name} collection: {str(e)}",
                cause=e,
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
            )

    def insert_one(self, data: Dict[str, Any]) -> str:
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise InternalServerError(
                message=f"Error creating document in {self.config.collection_name} collection: {str(e)}",
                cause=e,
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
            )

    def update_one(self, query: Dict[str, Any], data: Dict[str, Any]) -> int:
        try:
            result = self.collection.update_one(query, {"$set": data})
            return result.modified_count
        except Exception as e:
            raise InternalServerError(
                message=f"Error updating document in {self.config.collection_name} collection: {str(e)}",
                cause=e,
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
            )

    def delete_one(self, query: Dict[str, Any]) -> int:
        try:
            result = self.collection.delete_one(query)
            return result.deleted_count
        except Exception as e:
            raise InternalServerError(
                message=f"Error deleting document in {self.config.collection_name} collection: {str(e)}",
                cause=e,
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
            )


def get_base_repository(config: BaseRepositoryConfig) -> BaseRepository:
    return MongoBaseRepository(config)