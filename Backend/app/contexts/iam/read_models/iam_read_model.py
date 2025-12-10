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
    def get_by_id(self, user_id: ObjectId | str) -> dict | None:
        try:
            oid = mongo_converter.convert_to_object_id(user_id)
            cursor = self.collection.find_one({"_id": oid})
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
        page_size: int = 5,
    ) -> Tuple[List[dict], int]:
        try:
            # 1) Build query
            role_filter = roles if isinstance(roles, str) else {"$in": roles}
            query = {
                "deleted": {"$ne": True},
                "role": role_filter,
            }
            projection = {"password": 0}  # hide password

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

            # 3) Collect creator_ids (as strings or ObjectIds)
            creator_ids_raw = [
                u.get("created_by") for u in users if u.get("created_by")
            ]
            creator_ids_raw = list({cid for cid in creator_ids_raw})  # deduplicate

            # 4) Normalize to ObjectId list
            creator_oids = [
                mongo_converter.convert_to_object_id(cid)
                for cid in creator_ids_raw
                if cid is not None
            ]

            staff_map: Dict[str, str] = {}
            if creator_oids:
                # list_names_by_user_ids returns Dict[ObjectId, str]
                name_map = self.staff_read_model.list_names_by_user_ids(creator_oids)

                # convert ObjectId keys to str for easy lookup by created_by (string)
                staff_map = {str(user_id): name for user_id, name in name_map.items()}

            # 5) Attach creator_name
            for user in users:
                creator_id = user.get("created_by")  # usually a string
                creator_key = str(creator_id) if creator_id else None
                user["created_by_name"] = staff_map.get(creator_key, "Unknown")

            return users, total

        except Exception as e:
            self._handle_mongo_error("get_page_by_role", e)



    def count_active_users(self, role: str | list[str]) -> int:
        try:
            query = {"deleted": {"$ne": True}, "role": role}
            return self.collection.count_documents(query)
        except Exception as e:
            self._handle_mongo_error("count_active_users", e)