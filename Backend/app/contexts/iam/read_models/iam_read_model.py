from pymongo.database import Database
from typing import List , Tuple , Union
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.core.log.log_service import LogService
from bson import ObjectId
class IAMReadModel(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "users"):
        self.collection = db[collection_name]
        self.logger = LogService.get_instance() 
    def _log_operation(self, operation: str, info: str, detail: str = "", query: dict | None = None, result_count: int | None = None):
        self.logger.info(f"{operation} - {info} - {detail}")
        if query:
            self.logger.debug(f"Query: {query}")
        if result_count is not None:
            self.logger.info(f"Result count: {result_count}")


# -------------------------
# return raw for service
# -------------------------
    def get_by_id(self, user_id: ObjectId) -> dict | None:
        try:
            cursor = self.collection.find_one({"_id": user_id})
            self._log_operation("get_by_id", f"User ID: {user_id}")
            return cursor
        except Exception as e:
            self._handle_mongo_error("get_by_id", e)



    def get_by_email(self, email: str) -> dict | None:
        try:
            query = {"email": {"$regex": f"^{email}$", "$options": "i"}}
            result = self.collection.find_one(query)
            self._log_operation(
                "get_by_email",
                f"Lookup by email: {email}",
                query=query,
                result_count=1 if result else 0
            )
            return result
        except Exception as e:
            self._handle_mongo_error("get_by_email", e)

    def get_by_username(self, username: str) -> dict | None:
        try:
            query = {"username": {"$regex": f"^{username}$", "$options": "i"}}
            result = self.collection.find_one(query)
            self._log_operation(
                "get_by_username",
                f"Lookup by username: {username}",
                query=query,
                result_count=1 if result else 0
            )
            return result
        except Exception as e:
            self._handle_mongo_error("get_by_username", e)


    def get_page_by_role(
        self,
        roles: Union[str, list[str]],
        page: int = 1,
        page_size: int = 5
    ) -> Tuple[List[dict], int]:
        try:
            if isinstance(roles, str):
                query = {"deleted": {"$ne": True}, "role": roles}
            else:
                query = {"deleted": {"$ne": True}, "role": {"$in": roles}}
            projection = {"password": 0}
            total = self.collection.count_documents(query)
            skip = (page - 1) * page_size
            cursor = self.collection.find(query, projection).skip(skip).limit(page_size)
            users = list(cursor)

            self._log_operation(
                "get_page_by_role",
                f"Page {page} for roles: {roles}",
                query=query,
                result_count=len(users)
            )

            return users, total
        except Exception as e:
            self._handle_mongo_error("get_page_by_role", e)