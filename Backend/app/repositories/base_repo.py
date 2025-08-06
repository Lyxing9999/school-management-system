from abc import ABC, abstractmethod
from pymongo import ReturnDocument
from typing import Dict, List, Any, Union , TypeAlias 
from pymongo.database import Database
import logging
from pymongo.errors import DuplicateKeyError , PyMongoError
from app.utils.objectid import ObjectId
from app.error.exceptions import DatabaseError, ErrorCategory, ErrorSeverity, InternalServerError, PydanticValidationError , PydanticBaseValidationError
logger = logging.getLogger(__name__)
from bson.errors import InvalidId
from pymongo.collection import Collection as MongoCollection

Document: TypeAlias = Dict[str, Any]
Query: TypeAlias = Dict[str, Any]
Projection: TypeAlias = Dict[str, Any]

class BaseRepositoryConfig:
    def __init__(self, db: Database, collection_name: str, enable_logging: bool = True):
        self.db = db
        self.collection_name = collection_name    
        self.enable_logging = enable_logging
    
    def __repr__(self):
        return f"RepositoryConfig(db={self.db}, collection_name={self.collection_name}, enable_logging={self.enable_logging})"


class BaseRepository(ABC):
    @abstractmethod
    def find_all(self, projection: Projection | None = None, limit: int | None = None, skip: int | None = None, collection: MongoCollection | None = None) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def find_by_id(self, id: str, projection: Projection | None = None, collection: MongoCollection | None = None) -> Dict[str, Any] | None: ...

    @abstractmethod
    def find_by_query(self, query: Query, projection: Projection | None = None, collection: MongoCollection | None = None) -> Dict[str, Any] | None: ...

    @abstractmethod
    def find_many_by_query(self, query: Query, projection: Projection | None = None, limit: int | None = None, skip: int | None = None, collection: MongoCollection | None = None) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def insert_one(self, document: Document, collection: MongoCollection | None = None) -> str: ...

    @abstractmethod
    def insert_many(self, documents_list: List[Document], collection: MongoCollection | None = None) -> List[str]: ...

    @abstractmethod
    def delete_one(self, query: Query, collection: MongoCollection | None = None) -> int: ...

    @abstractmethod
    def delete_many(self, query: Query, collection: MongoCollection | None = None) -> int: ...

    @abstractmethod
    def update_one(self, query: Query, data: Dict[str, Any], collection: MongoCollection | None = None) -> int: ...

    @abstractmethod
    def update_many(self, query: Query, data: Dict[str, Any], collection: MongoCollection | None = None) -> int: ...

    @abstractmethod
    def count_documents(self, query: Query | None = None, collection: MongoCollection | None = None) -> int: ...

    @abstractmethod
    def exists(self, query: Query, collection: MongoCollection | None = None) -> bool: ...

    @abstractmethod
    def find_with_sort(self, query: Query, sort: List[tuple], projection: Projection | None = None, limit: int | None = None, skip: int | None = None, collection: MongoCollection | None = None) -> List[Dict[str, Any]]: ...

class MongoBaseRepository(BaseRepository):
    def __init__(self, config: BaseRepositoryConfig):
        self.config = config
        self.db = config.db
        self.collection = self.db[config.collection_name]
        self.logger = logger if config.enable_logging else None

    def _log_operation(self, operation: str, info: Any, detail: str = "", data: Dict[str, Any] | None = None):
        if self.logger:
            self.logger.info(f"{operation} {self.config.collection_name} info: {info} detail: {detail}")
            if data:
                self.logger.info(f"Data: {data}")

    def find_all(self, projection: Projection | None = None, limit: int | None = None, skip: int | None = None, collection: MongoCollection | None = None) -> List[Dict[str, Any]]:
        try:
            if collection is None:
                collection = self.collection 
            self._log_operation("find_all", f"projection: {projection}, limit: {limit}, skip: {skip}")
            cursor = collection.find({}, projection)
            if limit is not None:
                cursor = cursor.limit(limit)
            if skip is not None:
                cursor = cursor.skip(skip)

            return list(cursor)

        except Exception as e:
            self._handle_mongo_error("find_all", e, details=f"projection: {projection}, limit: {limit}, skip: {skip}")

    def find_by_query(self, query: Query, projection: Projection | None = None, collection: MongoCollection | None = None ) -> Dict[str, Any] | None:
        try:
            self._log_operation("find_by_query", f"query: {query}, projection: {projection} collection: {collection}")
            if collection is None:
                collection = self.collection 
            cursor = collection.find_one(query, projection)
            return cursor
        except Exception as e:
            self._handle_mongo_error("find_by_query", e)
    
        

    def find_many_by_query(self, query: Query, projection: Projection | None = None, limit: int | None = None, skip: int | None = None, collection: MongoCollection | None = None ) -> List[Dict[str, Any]]:
        try:
            self._log_operation("find_many_by_query", f"query: {query}, projection: {projection}, limit: {limit}, skip: {skip}")
            if collection is None:
                collection = self.collection 
            cursor = collection.find(query, projection)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("find_many_by_query", e)
    
    def find_by_id(self, id: str, projection: Projection | None = None, collection: MongoCollection | None = None ) -> Dict[str, Any] | None:
       try:
          self._log_operation("find_by_id", f"id: {id}, projection: {projection} collection: {collection}")
          if collection is None:
              collection = self.collection 
          cursor = collection.find_one({"_id": ObjectId(id)}, projection)
          return cursor
       except Exception as e:
          self._handle_mongo_error("find_by_id", e)
          
    def find_with_sort(self, query: Query, sort: List[tuple], projection: Projection | None = None, limit: int | None = None, skip: int | None = None, collection: MongoCollection | None = None) -> List[Dict[str, Any]]:
        try:
            if collection is None:
                collection = self.collection
            cursor = collection.find(query, projection).sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("find_with_sort", e) 
    
    def insert_one(self, document: Document, collection: MongoCollection | None = None ) -> str:
        try:
            self._log_operation("insert_one", f"data_keys={list(document.keys())}, collection: {collection}")
            if collection is None:
                collection = self.collection 
            result = collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            self._handle_mongo_error("insert_one", e)
    
    def insert_many(self, documents_list: List[Dict[str, Any]], collection: MongoCollection | None = None ) -> List[str]:
        try:
            self._log_operation("insert_many", f"count={len(documents_list)}, collection: {collection}")
            if collection is None:
                collection = self.collection
            result = collection.insert_many(documents_list)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            self._handle_mongo_error("insert_many", e)

    def update_one(self, query: Query, data: Dict[str, Any], collection: MongoCollection | None = None ) -> int:
        try:
            self._log_operation("update_one", f"query={query}")
            if collection is None:
                collection = self.collection
            result = collection.update_one(query, {"$set": data})
            return result.modified_count
        except Exception as e:
            self._handle_mongo_error("update_one", e)
        
    def update_many(self, query: Query, data: Dict[str, Any], collection: MongoCollection | None = None ) -> int:
        try: 
            self._log_operation("update_many", f"query={query}")
            if collection is None:
                collection = self.collection
            result = collection.update_many(query, {"$set": data})
            return result.modified_count
        except Exception as e:
            self._handle_mongo_error("update_many", e)
    
    def delete_one(self, query: Query, collection: MongoCollection | None = None ) -> int:
        try:
            self._log_operation("delete_one", f"query={query}")
            if collection is None:
                collection = self.collection
            result = collection.delete_one(query)
            return result.deleted_count
        except Exception as e:
            self._handle_mongo_error("delete_one", e)
    
    def delete_many(self, query: Dict[str, Any], collection: MongoCollection | None = None ) -> int:
        try:
            self._log_operation("delete_many", f"query={query}")
            if collection is None:
                collection = self.collection
            result = collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            self._handle_mongo_error("delete_many", e)
    
    def count_documents(self, query: Query | None = None, collection: MongoCollection | None = None ) -> int:
        try:
            query = query or {}
            self._log_operation("count_documents", f"query={query}")
            if collection is None:
                collection = self.collection
            return collection.count_documents(query)
        except Exception as e:
            self._handle_mongo_error("count_documents", e)
    
    def exists(self, query: Query, collection: MongoCollection | None = None ) -> bool:
        try:
            self._log_operation("exists", f"query={query}")
            if collection is None:
                collection = self.collection
            return collection.count_documents(query, limit=1) > 0
        except Exception as e:
            self._handle_mongo_error("exists", e)
        
    def insert_with_fetch(self, document: Dict[str, Any], projection: Projection | None = None, collection: MongoCollection | None = None) -> Dict[str, Any]:
        try:
            self._log_operation("insert_with_fetch", f"data_keys={list(document.keys())}")
            if collection is None:
                collection = self.collection
            result = collection.insert_one(document)
            doc = self.find_by_query({"_id": result.inserted_id}, projection=projection, collection=collection)
            if not doc:
                raise NotFoundError(message="Document not found after insert.", details={"inserted_id": str(result.inserted_id)}, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE)
            return doc
        except Exception as e:
            self._handle_mongo_error("insert_with_fetch", e)
    
    def update_with_fetch(self, query: Query, data: Dict[str, Any], collection: MongoCollection | None = None ) -> Dict[str, Any]:
        try:
            self._log_operation("update_with_fetch", f"query={query}, data_keys={list(data.keys())} collection: {collection}")
            if collection is None:
                collection = self.collection
            updated_doc = collection.find_one_and_update(
                query,
                {"$set": data},
                return_document=ReturnDocument.AFTER
            )
            return updated_doc
        except Exception as e:
            self._handle_mongo_error("update_with_fetch", e)
    
    
    def upsert_with_fetch(self, query: Query, data: Dict[str, Any], collection: MongoCollection | None =None) -> Dict[str, Any]:
        try:
            self._log_operation("upsert_with_fetch", f"query={query}, data_keys={list(data.keys())} collection: {collection}")
            if collection is None:
                collection = self.collection
            updated_doc = collection.find_one_and_update(
                query,
                {"$set": data},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            if updated_doc is None:
                raise DatabaseError(
                    message=f"Upsert operation failed in {self.config.collection} collection",
                    hint="Check query and data parameters",
                    status_code=500,
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.DATABASE,
                )
            return updated_doc
        except Exception as e:
            self._handle_mongo_error("upsert_with_fetch", e)
        
    def delete_with_fetch(self, query: Query, collection: MongoCollection | None = None ) -> Dict[str, Any] | None:
        try:
            self._log_operation("delete_with_fetch", f"query={query}")
            if collection is None:
                collection = self.collection
            return collection.find_one_and_delete(query)
        except Exception as e:
            self._handle_mongo_error("delete_with_fetch", e)
    
    def aggregate(self, pipeline: List[Dict[str, Any]], collection: MongoCollection | None = None ) -> List[Dict[str, Any]]:
        try:
            self._log_operation("aggregate", f"pipeline_states={len(pipeline)}")
            if collection is None:
                collection = self.collection
            return list(collection.aggregate(pipeline))
        except Exception as e:
            self._handle_mongo_error("aggregate", e)

    def create_index(self, keys: Union[str, List[tuple]], collection: MongoCollection | None = None, **kwargs) -> str:
        try:
            self._log_operation("create_index", f"keys={keys}")
            if collection is None:
                collection = self.collection
            return collection.create_index(keys, **kwargs)
        except Exception as e:
            self._handle_mongo_error("create_index", e)

    def list_indexes(self, collection: MongoCollection | None = None) -> List[Dict[str, Any]]:
        try:
            self._log_operation("list_indexes")
            if collection is None:
                collection = self.collection
            return list(collection.list_indexes())
        except Exception as e:
            self._handle_mongo_error("list_indexes", e)
            


    def _handle_mongo_error(self, operation: str, error: Exception, details: str = ""):
        error_message = f"Failed to {operation} {self.config.collection} with details: {details}"
        
        if isinstance(error, DuplicateKeyError):
            raise DatabaseError(
                message=f"{error_message}: Duplicate key error",
                cause=error,
                details={"operation": operation, "collection": self.config.collection, "details": details},
                hint="check for unique key violation",
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.DATABASE,
                status_code=409,
                user_message="An error occurred while processing your request. Please try again later.",
                recoverable=False, 
            )

        elif isinstance(error, InvalidId):
            raise DatabaseError(
                message=f"{error_message}: Invalid ObjectId format",
                cause=error,
                details={"operation": operation, "collection": self.config.collection, "details": details},
                hint="Check for valid MongoDB ObjectId format",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.DATABASE,
                status_code=400,
                user_message="The provided ID is invalid. Please check and try again.",
                recoverable=True, 
            )

        elif isinstance(error, PyMongoError):
            raise DatabaseError(
                message=f"{error_message}: MongoDB error - {str(error)}",
                cause=error,
                details={"operation": operation, "collection": self.config.collection, "details": details},
                hint="Check database connection and query syntax",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=500,
                user_message="An error occurred while processing your request. Please try again later.",
                recoverable=False,  
            )

        elif isinstance(error, PydanticValidationError):
            raise PydanticBaseValidationError(
                message=f"{error_message}: Pydantic validation error",
                cause=error,
                details={"operation": operation, "collection": self.config.collection, "details": details},
                hint="Check for valid data format",
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.VALIDATION,
                status_code=400,
                user_message="Invalid data provided. Please check your input and try again.",
                recoverable=True,
            )
        else:
            raise InternalServerError(
                message=f"{error_message}: {str(error)}",
                cause=error,
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                recoverable=False,
                user_message="An error occurred while processing your request. Please try again later.",
            )



class SQLBaseRepository(BaseRepository):
    def __init__(self, config: BaseRepositoryConfig):
        raise NotImplementedError("SQLBaseRepository is not implemented yet.")

class MockRepository(BaseRepository):
    def __init__(self, config: BaseRepositoryConfig):
        raise NotImplementedError("MockRepository is not implemented yet.")


class RepositoryFactory:
    @staticmethod
    def create_mongo_repository(config: BaseRepositoryConfig) -> BaseRepository:
        return MongoBaseRepository(config)

    @staticmethod
    def create_repository(config: BaseRepositoryConfig, repo_type: str = "mongo") -> BaseRepository:
        if repo_type.lower() == "mongo":
            return MongoBaseRepository(config)
        elif repo_type.lower() == "sql":
            return SQLBaseRepository(config)  
        elif repo_type.lower() == "mock":
            return MockRepository(config)   
        else:
            raise ValueError(f"Unsupported repository type: {repo_type}")


def get_base_repository(config: BaseRepositoryConfig) -> BaseRepository:
    return RepositoryFactory.create_repository(config)