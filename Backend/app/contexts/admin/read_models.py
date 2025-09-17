
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from pymongo.database import Database
from bson import ObjectId
from typing import List , Tuple , Union
class AdminReadModel(MongoErrorMixin):
    def __init__(self, db: Database , collection_name: str = "users" , collection_staff: str = "staff" , collection_classes: str = "classes" ):
        self.db = db
        self.collection_users = db[collection_name]
        self.collection_staff = db[collection_staff]
        self.collection_classes = db[collection_classes]
        self.mongo_converter = mongo_converter


    

    def get_page_by_role(self, roles: Union[str, list[str]], page: int = 1, page_size: int = 5) -> Tuple[List[dict], int]:
        try:
            if isinstance(roles, str):
                query = {"deleted": {"$ne": True}, "role": roles}
            else:
                query = {"deleted": {"$ne": True}, "role": {"$in": roles}}
            projection = {"password": 0}
            total = self.collection_users.count_documents(query)
            skip = (page - 1) * page_size
            cursor = self.collection_users.find(query, projection).skip(skip).limit(page_size)
            users = list(cursor)
            return users, total
        except Exception as e:
            self._handle_mongo_error("get_page_by_role", e)



    def get_staff_by_id(self, staff_id: ObjectId) -> dict:
        try:
            cursor = self.collection_staff.find_one({"_id": staff_id})
            return cursor
        except Exception as e:
            self._handle_mongo_error("get_staff_by_id", e)
            return {}
