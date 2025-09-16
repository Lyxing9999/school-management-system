from pymongo.database import Database
from app.contexts.shared.enum.roles import UserRole
from app.contexts.iam.data_transfer.responses import UserResponseDataDTO , UserResponseDataDTOList , UserSelectDataDTO , UserSelectDataDTOList , UserReadDataDTO , UserReadDataDTOList 
from typing import List , Tuple , Union
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from bson import ObjectId
from app.contexts.shared.model_converter import ModelConverterUtils
import logging

logger = logging.getLogger(__name__)

class UserReadModel(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "users"):
        self.collection = db[collection_name]
        self.mongo_converter = mongo_converter

    def _log_operation(self, operation: str, info: str, detail: str = "", query: dict | None = None, result_count: int | None = None):
        logger.info(f"{operation} - {info} - {detail}")
        if query:
            logger.debug(f"Query: {query}")
        if result_count is not None:
            logger.info(f"Result count: {result_count}")


# -------------------------
# return raw for service
# -------------------------
    def get_by_id(self, user_id: ObjectId) -> dict:
        try:
            cursor = self.collection.find_one({"_id": user_id})
            self._log_operation("get_by_id", f"User ID: {user_id}")
            return cursor
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)

    def get_by_username(self, username: str) -> dict:
        try:
            cursor = self.collection.find_one({"username": username})
            self._log_operation("get_by_username", f"Username: {username}")
            return cursor
        except Exception as e:
            self._handle_mongo_error("get_by_username", e)
    def get_by_email(self, email: str) -> dict:
        try:
            cursor = self.collection.find_one({"email": email})
            self._log_operation("get_by_email", f"Email: {email}")
            return cursor
        except Exception as e:
            self._handle_mongo_error("get_by_email", e)


# -------------------------
# return DTO for response
# -------------------------

    def get_all_users(self) -> UserReadDataDTOList:
        try:
            cursor = self.collection.find({"deleted": {"$ne": True}})
            users = self.mongo_converter.cursor_to_dto(cursor, UserReadDataDTO)
            self._log_operation("get_all_users", "Get all users")
            return UserReadDataDTOList(users)
        except Exception as e:
            self._handle_mongo_error("get_all_users", e)

    

    def get_page_by_role(self, roles: Union[str, list[str]], page: int = 1, page_size: int = 5) -> Tuple[List[dict], int]:
        if isinstance(roles, str):
            query = {"deleted": {"$ne": True}, "role": roles}
        else:
            query = {"deleted": {"$ne": True}, "role": {"$in": roles}}
        projection = {"password": 0}
        total = self.collection.count_documents(query)
        skip = (page - 1) * page_size
        cursor = self.collection.find(query, projection).skip(skip).limit(page_size)
        users = list(cursor)
        return users, total






    def get_all_teachers_for_select(self) -> List[dict]:
        try:
            cursor = self.collection.find({"role": UserRole.TEACHER.value}, {"_id": 1, "username": 1, "email": 1})
            users = self.mongo_converter.cursor_to_dto(cursor, UserSelectDataDTO)
            self._log_operation("get_all_teachers_for_select", "Get all teachers")
            return users
        except Exception as e:
            self._handle_mongo_error("get_all_teachers_for_select", e)



