from __future__ import annotations

from datetime import datetime, timedelta
from bson import ObjectId
from enum import Enum
from app.contexts.auth.services import get_auth_service

from app.contexts.shared.enum.roles import SystemRole
from app.contexts.iam.error.iam_exceptions import InvalidRoleException
from app.contexts.iam.data_transfer.responses import IAMBaseDataDTO
from app.contexts.iam.error.iam_exceptions import UserDeletedException

# -------------------------
# Domain Model
# -------------------------
class IAM:
    def __init__(
        self,
        email: str,
        password: str,
        role: SystemRole,
        id: ObjectId | None = None,
        username: str | None = None,
        created_by: ObjectId | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        deleted: bool = False,
        deleted_at: datetime | None = None,
        deleted_by: ObjectId | None = None
    ):
        self.id = id or ObjectId()
        self._email = email
        self._password = password
        self._role = self._validate_role(role)
        self._username = username
        self.created_by = created_by or "self_created"
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by

    # ---------- Properties ----------
    @property
    def email(self) -> str:
        return self._email

    @property
    def username(self) -> str | None:
        return self._username

    @username.setter
    def username(self, value: str | None):
        self._username = value
        self._mark_updated()

    @property
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = value
        self._mark_updated()

    @property
    def role(self) -> SystemRole:
        return self._role

    @role.setter
    def role(self, value: SystemRole):
        self._role = self._validate_role(value)
        self._mark_updated()

    # ---------- Methods ----------
    def _mark_updated(self):
        self.updated_at = datetime.utcnow()

    def check_password(self, password: str, auth_service) -> bool:
        return auth_service.verify_password(password, self._password)

    def update_info(self, email: str | None = None, username: str | None = None, password: str | None = None):
        if self.is_deleted():
            raise UserDeletedException(self.id)
        updated = False
        if email is not None:
            self._email = email
            updated = True
        if username is not None:
            self._username = username
            updated = True
        if password is not None:
            self._password = password
            updated = True
        if updated:
            self._mark_updated()

    def is_deleted(self) -> bool:
        return self.deleted

    def soft_delete(self, deleted_by: ObjectId):
        if self.deleted:
            return False
        self.deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by
        self._mark_updated()
        return True

    def ready_for_purge(self, days: int = 30) -> bool:
        return self.deleted and self.deleted_at and self.deleted_at < datetime.utcnow() - timedelta(days=days)

    @staticmethod
    def _validate_role(role: Enum | str) -> SystemRole:
        """
        Accept SystemRole, UserRole, StaffRole, or string.
        Normalize into SystemRole.
        """
        try:
            if isinstance(role, SystemRole):
                return role
            if isinstance(role, str):
                return SystemRole(role)
            if isinstance(role, Enum):
                return SystemRole(role.value)
            raise InvalidRoleException(role)
        except ValueError:
            raise InvalidRoleException(role)


# -------------------------
# Factory
# -------------------------
class IAMFactory:
    def __init__(self, user_read_model, auth_service=None):
        self.user_read_model = user_read_model
        self.auth_service = auth_service or get_auth_service()

    def create_user(
        self,
        email: str,
        password: str,
        username: str | None = None,
        role: SystemRole | None = None,
        created_by: str | None = None
    ) -> IAM:
        role = role or SystemRole.STUDENT
        username = self._generate_unique_username(username or email.split("@")[0])
        hashed_password = self.auth_service.hash_password(password)
        created_by = created_by or "self_created"
        
        return IAM(
            email=email,
            password=hashed_password,
            username=username,
            role=role,
            created_by=created_by
        )

    def _generate_unique_username(self, base_username: str) -> str:
        username = base_username
        counter = 1
        while self.user_read_model.get_by_username(username):
            username = f"{base_username}{counter}"
            counter += 1
        return username


# -------------------------
# Mapper
# -------------------------
class IAMMapper:
    @staticmethod
    def to_domain(data: dict) -> IAM:
        if isinstance(data, IAM):
            return data

        id_value = data.get("_id") or data.get("id") or ObjectId()
        if id_value and not isinstance(id_value, ObjectId):
            id_value = ObjectId(id_value)

        return IAM(
            id=id_value,
            email=data["email"],
            password=data["password"],
            role=IAM._validate_role(data["role"]),
            username=data.get("username"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deleted=data.get("deleted", False),
            deleted_at=data.get("deleted_at"),
            deleted_by=data.get("deleted_by")
        )

    @staticmethod
    def to_persistence(iam: IAM) -> dict:
        return {
            "_id": iam.id,
            "email": iam.email,
            "password": iam.password,
            "role": iam.role.value,
            "username": iam.username,
            "created_by": iam.created_by,
            "created_at": iam.created_at,
            "updated_at": iam.updated_at,
            "deleted_at": iam.deleted_at,
            "deleted": iam.deleted,
            "deleted_by": iam.deleted_by
        }

    @staticmethod
    def to_safe_dict(iam: IAM) -> dict:
        return {
            "id": str(iam.id),
            "email": iam.email,
            "username": iam.username,
            "role": iam.role.value,
            "created_by": str(iam.created_by),
            "created_at": iam.created_at,
            "updated_at": iam.updated_at,
            "deleted": iam.deleted,
            "deleted_by": str(iam.deleted_by)
        }

    @staticmethod
    def to_dto(iam: IAM) -> IAMBaseDataDTO:
        return IAMBaseDataDTO(
            id=str(iam.id),
            email=iam.email,
            username=iam.username,
            role=iam.role.value,
            created_by=str(iam.created_by),
            created_at=iam.created_at,
            updated_at=iam.updated_at,
            deleted=iam.deleted,
            deleted_by=str(iam.deleted_by)
        )