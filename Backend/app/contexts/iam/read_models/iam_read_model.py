from __future__ import annotations
from pymongo.database import Database
from typing import List , Tuple , Union, Dict
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.core.log.log_service import LogService
from bson import ObjectId
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.staff.read_model import StaffReadModel
class IAMReadModel(MongoErrorMixin):
    def __init__(self, db: Database, collection_name: str = "users"):
        self.db = db
        self.collection = db[collection_name]
        self._staff_read_model: StaffReadModel | None = None
        self.logger = LogService.get_instance() 
    def _log_operation(self, operation: str, info: str, detail: str = "", query: dict | None = None, result_count: int | None = None):
        self.logger.info(f"{operation} - {info} - {detail}")
        if query:
            self.logger.debug(f"Query: {query}")
        if result_count is not None:
            self.logger.info(f"Result count: {result_count}")

    @property
    def staff_read_model(self) -> StaffReadModel:
        if self._staff_read_model is None:
            self._staff_read_model = StaffReadModel(self.db)
        return self._staff_read_model

    def list_usernames_by_role(self, role: str) -> List[dict]:
        """
        Return [{ _id, username }] for active users with this role.
        Used for dropdowns, etc.
        """
        try:
            cursor = self.collection.find(
                {"role": role, "deleted": {"$ne": True}},
                {"username": 1, "_id": 1},
            )
            return list(cursor)
        except Exception as e:
            self._handle_mongo_error("list_usernames_by_role", e)
            return []

    def list_usernames_by_ids(self, user_ids: List[ObjectId], role: str) -> List[dict]:
        """
        Given a list of user ObjectIds, return [{_id, username}, ...] 

        """
        if not user_ids:
            return []

        cursor = self.collection.find(
            {
                "_id": {"$in": user_ids},
                "role": role,
                "deleted": {"$ne": True},
            },
            {"username": 1}  
        )
        return list(cursor)
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
            role_filter = roles if isinstance(roles, str) else {"$in": roles}
            query = {"deleted": {"$ne": True}, "role": role_filter}
            projection = {"password": 0}  

            # 2) Count + pagination
            total = self.collection.count_documents(query)
            skip = (page - 1) * page_size

            users: List[Dict[str, Any]] = list(
                self.collection.find(query, projection)
                .sort("created_at", -1)
                .skip(skip)
                .limit(page_size)
            )

            if not users:
                return users, total

            # 3) Collect creator IDs (strings)
            creator_ids_raw = [
                u.get("created_by") for u in users 
                if u.get("created_by")
            ]

            # Deduplicate
            creator_ids_raw = list({cid for cid in creator_ids_raw})

            # 4) Convert to ObjectId because staff.user_id is probably ObjectId
            creator_oids = [
                mongo_converter.convert_to_object_id(cid)
                for cid in creator_ids_raw
            ]

            staff_map: Dict[str, str] = {}
            if creator_oids:
                staff_cursor = self.staff_read_model.list_by_user_ids(creator_oids)

                # key = string of ObjectId, value = staff_name
                for staff in staff_cursor:
                    key = str(staff["user_id"])
                    staff_map[key] = staff.get("staff_name", "Unknown")

            # 5) Attach creator name (or override created_by if you like)
            for user in users:
                creator_id = user.get("created_by")  # string
                creator_key = str(creator_id) if creator_id else None
                user["created_by_name"] = staff_map.get(creator_key, "Unknown")

                # If you want to REPLACE created_by by staff_name:
                # user["created_by"] = user["created_by_name"]

 

            return users, total

        except Exception as e:
            self._handle_mongo_error("get_page_by_role", e)