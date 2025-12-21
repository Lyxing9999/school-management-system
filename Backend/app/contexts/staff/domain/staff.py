from dataclasses import dataclass, field
from typing import Optional, List
from bson import ObjectId

from app.contexts.shared.enum.roles import SystemRole
from app.contexts.shared.lifecycle.domain import Lifecycle
from .value_objects import  StaffName, PhoneNumber

from app.contexts.staff.errors.staff_exceptions import (
    InvalidStaffRoleException,
    StaffRoleNotAllowedException,
)
from enum import Enum
@dataclass
class Staff:
    id: ObjectId = field(default_factory=ObjectId)
    user_id: Optional[ObjectId] = None

    staff_id: str = field(default=None)
    staff_name: StaffName = field(default=None)
    role: SystemRole = SystemRole.TEACHER

    phone_number: Optional[PhoneNumber] = None
    address: str = ""
    permissions: List[str] = field(default_factory=list)

    created_by: Optional[ObjectId] = None
    lifecycle: Lifecycle = field(default_factory=Lifecycle)

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def touch(self):
        self.lifecycle.touch()

    def soft_delete(self, actor_id: ObjectId) -> bool:
        return self.lifecycle.soft_delete(actor_id)

    def restore(self):
        self.lifecycle.restore()

    @staticmethod
    def validate_role(role: SystemRole | str | Enum) -> SystemRole:
        if role is None:
            raise InvalidStaffRoleException(role)

        # Convert input -> SystemRole
        if isinstance(role, SystemRole):
            normalized = role

        elif isinstance(role, str):
            r = role.strip().lower()
            if not r:
                raise InvalidStaffRoleException(role)
            try:
                normalized = SystemRole(r)
            except ValueError as ex:
                raise InvalidStaffRoleException(role) from ex

        elif isinstance(role, Enum):
            try:
                normalized = SystemRole(str(role.value).strip().lower())
            except ValueError as ex:
                raise InvalidStaffRoleException(role) from ex

        else:
            raise InvalidStaffRoleException(role)

        # Staff domain policy: allow only staff roles
        allowed = {SystemRole.ADMIN, SystemRole.TEACHER}
        if normalized not in allowed:
            raise StaffRoleNotAllowedException(
                role=normalized.value,
                allowed=sorted([r.value for r in allowed]),
            )

        return normalized