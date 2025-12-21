from __future__ import annotations

from datetime import datetime, timedelta
from bson import ObjectId
from enum import Enum
from app.contexts.shared.enum.roles import SystemRole
from app.contexts.iam.error.iam_exception import InvalidRoleException, UserDeletedException
from app.contexts.shared.lifecycle.domain import Lifecycle  


class IAMStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"


class IAM:
    def __init__(
        self,
        email: str,
        password: str,
        role: SystemRole,
        id: ObjectId | None = None,
        username: str | None = None,
        created_by: ObjectId | None = None,
        status: IAMStatus | str = IAMStatus.ACTIVE,
        lifecycle: Lifecycle | None = None,
    ):
        self.id = id or ObjectId()
        self._email = email
        self._password = password
        self._role = self._validate_role(role)
        self._username = username
        self.created_by = created_by or "self_created"
        self.status = IAMStatus(status) if isinstance(status, str) else status
        self.lifecycle = lifecycle or Lifecycle()

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

    # ---------- Lifecycle-backed timestamps ----------
    @property
    def created_at(self) -> datetime:
        return self.lifecycle.created_at

    @property
    def updated_at(self) -> datetime:
        return self.lifecycle.updated_at

    def _mark_updated(self):
        self.lifecycle.touch()

    # ---------- Business ----------
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

    # ---------- Delete / Restore ----------
    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def soft_delete(self, actor_id: ObjectId):
        self.lifecycle.soft_delete(actor_id)

    def restore(self):
        self.lifecycle.restore()

    # ---------- Status (IAM domain, not lifecycle) ----------
    def is_active(self) -> bool:
        return (not self.is_deleted()) and self.status == IAMStatus.ACTIVE

    def is_inactive(self) -> bool:
        return self.status == IAMStatus.DISABLED

    def set_status(self, status: IAMStatus | str):
        if self.is_deleted():
            raise UserDeletedException(self.id)
        self.status = IAMStatus(status) if isinstance(status, str) else status
        self._mark_updated()

    # ---------- Purge helper ----------
    def ready_for_purge(self, days: int = 30) -> bool:
        if not self.is_deleted() or self.lifecycle.deleted_at is None:
            return False
        return self.lifecycle.deleted_at < datetime.utcnow() - timedelta(days=days)

    @staticmethod
    def _validate_role(role: Enum | str) -> SystemRole:
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