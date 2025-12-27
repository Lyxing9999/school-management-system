from __future__ import annotations
from pymongo.database import Database
from typing import List , Tuple , Union, Dict, Final, Any
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from bson import ObjectId
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.staff.read_models.staff_read_model import StaffReadModel

from app.contexts.shared.lifecycle.filters import not_deleted, active


class IAMReadModel(MongoErrorMixin):
    def __init__(self, db: Database):
        self.db = db
        self.collection = db["iam"]
        self._staff_read_model: Final[StaffReadModel] = StaffReadModel(db)






    def find_one(self, query: dict) -> dict | None:
        """Find a single user matching the query."""
        return self.collection.find_one(query)


 
    def list_usernames_by_role(self, role: str) -> List[dict]:
        """
        Return [{ _id, username }] for active users with this role.
        Used for dropdowns, etc.
        """
        return list(self.collection.find(
                active({"role": role}),
                {"username": 1, "_id": 1},
            )
        )


    def list_usernames_by_ids(self, user_ids: List[ObjectId], role: str) -> List[dict]:
        """
        Given a list of user ObjectIds, return [{_id, username}, ...] 
        """
        if not user_ids:
            return []
        return list(
            self.collection.find(
                active({"_id": {"$in": user_ids},"role": role}),
                {"username": 1}
            )
        )


    # -------------------------
    # return raw for service
    # -------------------------

    def get_by_id(self, user_id: ObjectId | str) -> dict | None:
        oid = mongo_converter.convert_to_object_id(user_id)
        return self.collection.find_one({"_id": oid})

    def get_active_by_id(self, user_id: ObjectId | str) -> dict | None:
        oid = mongo_converter.convert_to_object_id(user_id)
        return self.collection.find_one(active({"_id": oid}))
        
    def get_by_email(self, email: str) -> dict | None:
        query = {"email": {"$regex": f"^{email}$", "$options": "i"}}
        result = self.collection.find_one(query)
        return result


    def get_by_username(self, username: str) -> dict | None:
        query = {"username": {"$regex": f"^{username}$", "$options": "i"}}
        result = self.collection.find_one(query)
        return result



    def get_page_by_role(
        self,
        roles: Union[str, list[str]],
        page: int = 1,
        page_size: int = 5,
        search: str | None = None,
    ) -> Tuple[List[dict], int]:

        role_filter = roles if isinstance(roles, str) else {"$in": roles}

        base: Dict[str, Any] = {"role": role_filter}

        if search and (s := search.strip()):
            base["$or"] = [
                {"username": {"$regex": s, "$options": "i"}},
                {"email": {"$regex": s, "$options": "i"}},
                {"phone": {"$regex": s, "$options": "i"}},
            ]

        query = not_deleted(base)
        projection = {"password": 0}

        total = self.collection.count_documents(query)
        skip = (page - 1) * page_size

        users: List[Dict[str, Any]] = list(
            self.collection.find(query, projection)
            .sort("lifecycle.created_at", -1)
            .skip(skip)
            .limit(page_size)
        )
        if not users:
            return users, total

        creator_ids_raw = [u.get("created_by") for u in users if u.get("created_by")]
        creator_ids_raw = list({cid for cid in creator_ids_raw})

        creator_oids = [
            mongo_converter.convert_to_object_id(cid)
            for cid in creator_ids_raw
            if cid is not None
        ]

        staff_map: Dict[str, str] = {}
        if creator_oids:
            name_map = self._staff_read_model.list_names_by_ids(creator_oids)
            staff_map = {str(user_id): name for user_id, name in name_map.items()}

        for user in users:
            creator_id = user.get("created_by")
            creator_key = str(creator_id) if creator_id else None
            user["created_by_name"] = staff_map.get(creator_key, "Unknown")

        return users, total






    def count_active_users(self, role: str | list[str]) -> int:
        return self.collection.count_documents(active({"role": role}))