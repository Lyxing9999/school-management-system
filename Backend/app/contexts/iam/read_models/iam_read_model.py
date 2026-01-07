from typing import Any, Dict, List, Tuple, Union, Final, Optional

from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.shared.lifecycle.filters import ShowDeleted, active, by_show_deleted
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
from app.contexts.iam.domain.iam import IAMStatus

ACTIVE_IAM_STATUS = IAMStatus.ACTIVE.value


class IAMReadModel(MongoErrorMixin):
    def __init__(self, db: Database):
        self.db = db
        self.collection = db["iam"]
        self._staff_read_model: Final[StaffReadModel] = StaffReadModel(db)

    def _oid(self, v: ObjectId | str | None) -> ObjectId | None:
        if v is None:
            return None
        return mongo_converter.convert_to_object_id(v)

    def find_one(self, query: dict, *, show_deleted: ShowDeleted = "active") -> dict | None:
        return self.collection.find_one(by_show_deleted(show_deleted, dict(query or {})))


    def list_usernames_by_role(self, role: str) -> List[dict]:
        return list(
            self.collection.find(
                active({"role": role, "status": ACTIVE_IAM_STATUS}),
                {"username": 1, "_id": 1},
            )
        )

    def list_usernames_by_ids(self, user_ids: List[ObjectId], role: str) -> List[dict]:
        if not user_ids:
            return []
        return list(
            self.collection.find(
                active({"_id": {"$in": user_ids}, "role": role, "status": ACTIVE_IAM_STATUS}),
                {"username": 1},
            )
        )

    def get_by_id(self, user_id: ObjectId | str, *, show_deleted: ShowDeleted = "active") -> dict | None:
        oid = self._oid(user_id)
        if not oid:
            return None
        return self.collection.find_one(by_show_deleted(show_deleted, {"_id": oid}))

    def get_active_by_id(self, user_id: ObjectId | str) -> dict | None:
        oid = self._oid(user_id)
        if not oid:
            return None
        return self.collection.find_one(active({"_id": oid, "status": ACTIVE_IAM_STATUS}))

    def get_by_email(self, email: str, *, show_deleted: ShowDeleted = "active") -> dict | None:
        e = (email or "").strip()
        if not e:
            return None
        query = {"email": {"$regex": f"^{e}$", "$options": "i"}}
        return self.collection.find_one(by_show_deleted(show_deleted, query))

    def get_by_username(self, username: str, *, show_deleted: ShowDeleted = "active") -> dict | None:
        u = (username or "").strip()
        if not u:
            return None
        query = {"username": {"$regex": f"^{u}$", "$options": "i"}}
        return self.collection.find_one(by_show_deleted(show_deleted, query))

    def get_page_by_role(
        self,
        roles: Union[str, list[str]],
        page: int = 1,
        page_size: int = 5,
        search: str | None = None,
        *,
        show_deleted: ShowDeleted = "active",
        status: str | None = None,  
    ) -> Tuple[List[dict], int]:
        role_filter = roles if isinstance(roles, str) else {"$in": roles}

        base: Dict[str, Any] = {"role": role_filter}
        if status:
            base["status"] = status

        if search and (s := search.strip()):
            base["$or"] = [
                {"username": {"$regex": s, "$options": "i"}},
                {"email": {"$regex": s, "$options": "i"}},
                {"phone": {"$regex": s, "$options": "i"}},
            ]

        query = by_show_deleted(show_deleted, base)
        projection = {"password": 0}

        page = max(1, int(page))
        page_size = min(max(1, int(page_size)), 100)
        skip = (page - 1) * page_size

        total = self.collection.count_documents(query)

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

        creator_oids = [self._oid(cid) for cid in creator_ids_raw if cid is not None]
        creator_oids = [oid for oid in creator_oids if oid is not None]

        staff_map: Dict[str, str] = {}
        if creator_oids:
            name_map = self._staff_read_model.list_names_by_ids(creator_oids)
            staff_map = {str(user_id): name for user_id, name in name_map.items()}

        for user in users:
            creator_id = user.get("created_by")
            creator_key = str(creator_id) if creator_id else None
            user["created_by_name"] = staff_map.get(creator_key, "Unknown")

        return users, total


    # -------------------------
    # Fix 1 continued: count must include ACTIVE status too
    # -------------------------
    def count_active_users(self, role: str | list[str]) -> int:
        return self.collection.count_documents(active({"role": role, "status": ACTIVE_IAM_STATUS}))

    def list_active_user_ids_by_role(self, role: str) -> List[ObjectId]:
        cursor = self.collection.find(
            active({"role": role, "status": ACTIVE_IAM_STATUS}),
            {"_id": 1},
        )
        return [doc["_id"] for doc in cursor if doc.get("_id")]