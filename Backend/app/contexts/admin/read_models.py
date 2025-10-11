
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from pymongo.database import Database
from bson import ObjectId
from typing import List , Tuple , Union , Optional
from app.contexts.iam.read_models import IAMReadModel
from app.contexts.staff.read_models import StaffReadModel
class AdminReadModel(MongoErrorMixin):
    def __init__(self, db: Database , collection_users: str = "users" , collection_staff: str = "staff" , collection_classes: str = "classes" ):
        self.db = db
        self.collection_users = db[collection_users]
        self.collection_staff = db[collection_staff]
        self.collection_classes = db[collection_classes]
        self.mongo_converter = mongo_converter
        self._iam_read_model: Optional[IAMReadModel] = None
        self._staff_read_model: Optional[StaffReadModel] = None

    @property
    def iam_read_model(self) -> IAMReadModel:
        if self._iam_read_model is None:
            self._iam_read_model = IAMReadModel(self.db)
        return self._iam_read_model

    @property
    def staff_read_model(self) -> StaffReadModel:
        if self._staff_read_model is None:
            self._staff_read_model = StaffReadModel(self.db)
        return self._staff_read_model

    def get_page_by_role(
        self, 
        roles: Union[str, list[str]], 
        page: int = 1, 
        page_size: int = 5
    ) -> Tuple[List[dict], int]:
        """
        Get paginated users filtered by role(s), with human-readable creator name.

        Args:
            roles (str | list[str]): Role or list of roles to filter.
            page (int): Page number (1-based).
            page_size (int): Number of users per page.

        Returns:
            Tuple[List[dict], int]: List of user dicts and total user count.
        """
        try:
            # Prepare role filter
            role_filter = roles if isinstance(roles, str) else {"$in": roles}
            query = {"deleted": {"$ne": True}, "role": role_filter}
            projection = {"password": 0}  # Exclude password

            # Count total matching users
            total = self.collection_users.count_documents(query)

            # Pagination
            skip = (page - 1) * page_size
            users = list(
                self.collection_users.find(query, projection)
                .sort("created_at", -1)
                .skip(skip)
                .limit(page_size)
            )

            # Get all creator IDs
            creator_ids = [user["created_by"] for user in users if user.get("created_by")]

            # Map user_id → staff_name
            staff_map = {}
            if creator_ids:
                staff_cursor = self.collection_staff.find({"user_id": {"$in": creator_ids}})
                staff_map = {str(staff["user_id"]): staff["staff_name"] for staff in staff_cursor}

            # Add human-readable creator name
            for user in users:
                user["created_by_name"] = staff_map.get(str(user.get("created_by")), "Unknown")
            return users, total

        except Exception as e:
            self._handle_mongo_error("get_page_by_role", e)




    def get_staff_by_id(self, staff_id: ObjectId) -> Optional[dict]:
        return self.staff_read_model.get_by_id(staff_id)

    def get_user_by_id(self, user_id: ObjectId) -> Optional[dict]:
        return self.iam_read_model.get_by_id(user_id)