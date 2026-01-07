from dataclasses import dataclass, field
from typing import Optional, List, Any
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
        allowed = {SystemRole.ACADEMIC, SystemRole.TEACHER}
        if normalized not in allowed:
            raise StaffRoleNotAllowedException(
                role=normalized.value,
                allowed=sorted([r.value for r in allowed]),
            )

        return normalized


    def update_staff_patch(self, payload: Any, staff_repo=None) -> None:
        """
        Apply partial updates with validation + change detection.
        `payload` can be Pydantic model (v1/v2) or dict.
        `staff_repo` is optional for invariants like uniqueness checks.
        """

        patch = self._normalize_patch(payload)

        # allow only these keys to be updated via PATCH
        allowed = {"staff_id", "staff_name", "role", "phone_number", "address", "permissions", "user_id"}
        patch = {k: v for k, v in patch.items() if k in allowed}

        if not patch:
            raise StaffNoChangeAppException("No fields provided for update")

        changed = False

        # user_id
        if "user_id" in patch:
            new_user_id = patch["user_id"]
            if new_user_id != self.user_id:
                self.user_id = new_user_id
                changed = True

        # staff_id (optional uniqueness check)
        if "staff_id" in patch and patch["staff_id"] is not None:
            new_staff_id = str(patch["staff_id"]).strip()
            if new_staff_id and new_staff_id != self.staff_id:
                # Optional invariant: ensure staff_id unique
                if staff_repo and hasattr(staff_repo, "exists_by_staff_id"):
                    if staff_repo.exists_by_staff_id(new_staff_id, exclude_id=self.id):
                        raise ValueError(f"staff_id '{new_staff_id}' already exists")  # replace with your exception
                self.staff_id = new_staff_id
                changed = True

        # staff_name
        if "staff_name" in patch and patch["staff_name"] is not None:
            new_name = StaffName(str(patch["staff_name"]))
            if new_name != self.staff_name:
                self.staff_name = new_name
                changed = True

        # role
        if "role" in patch and patch["role"] is not None:
            new_role = self.validate_role(patch["role"])
            if new_role != self.role:
                self.role = new_role
                changed = True

        # phone_number (allow clearing by passing empty string / None if you want)
        if "phone_number" in patch:
            raw = patch["phone_number"]
            if raw in (None, ""):
                if self.phone_number is not None:
                    self.phone_number = None
                    changed = True
            else:
                new_phone = PhoneNumber(str(raw))
                if new_phone != self.phone_number:
                    self.phone_number = new_phone
                    changed = True

        # address
        if "address" in patch and patch["address"] is not None:
            new_address = str(patch["address"])
            if new_address != self.address:
                self.address = new_address
                changed = True

        # permissions
        if "permissions" in patch and patch["permissions"] is not None:
            new_perms = list(patch["permissions"])
            if new_perms != self.permissions:
                self.permissions = new_perms
                changed = True

        if not changed:
            raise StaffNoChangeAppException("Staff already up-to-date")

        self.touch()

    @staticmethod
    def _normalize_patch(payload: Any) -> dict:
        """
        Supports:
        - dict
        - Pydantic v2: model_dump(exclude_unset=True)
        - Pydantic v1: dict(exclude_unset=True)
        """
        if payload is None:
            return {}

        if isinstance(payload, dict):
            return payload

        # Pydantic v2
        if hasattr(payload, "model_dump"):
            return payload.model_dump(exclude_unset=True)

        # Pydantic v1
        if hasattr(payload, "dict"):
            return payload.dict(exclude_unset=True)

        # fallback: try to read __dict__
        if hasattr(payload, "__dict__"):
            return dict(payload.__dict__)

        return {}