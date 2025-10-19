from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.contexts.shared.enum.roles import StaffRole, SystemRole
from app.contexts.core.policy.policy_service import PolicyService
from app.contexts.staff.error.staff_exceptions import (
    InvalidStaffRoleException,
    NoChangeAppException,
    StaffPermissionException,
    StaffNoChangeAppException,
    StaffAlreadyExistsAppException
)
from app.contexts.staff.data_transfer.requests import (
    StaffCreateSchema,
    StaffUpdateSchema,
)
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO


# ============================================================
# Aggregate Root: Staff
# ============================================================
class Staff:
    """
    Staff Aggregate — represents a staff member in the HR bounded context.
    Contains domain logic related to permissions, updates, and lifecycle.
    """

    _policy_service = PolicyService(
        config_path="app/contexts/core/policy/config/policies.json"
    )

    def __init__(
        self,
        staff_id: str,
        staff_name: str,
        role: SystemRole,
        phone_number: str,
        id: Optional[ObjectId] = None,
        user_id: Optional[ObjectId] = None,
        permissions: Optional[List[str]] = None,
        address: Optional[str] = None,
        created_by: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,
        deleted: bool = False,
        deleted_by: Optional[ObjectId] = None,
    ):
        self.id = id or ObjectId()
        self.user_id = user_id
        self.staff_id = staff_id
        self.staff_name = staff_name
        self.phone_number = phone_number
        self.address = address or ""
        self.role = role
        self.permissions = (
            permissions
            if permissions is not None
            else self._policy_service.get_default_permissions(role)
        )
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted
        self.deleted_at = deleted_at
        self.deleted_by = deleted_by

    # ============================================================
    # Domain Behavior
    # ============================================================

    def grant_permission(self, permission: str):
        """Add a permission if not already granted."""
        if permission not in self.permissions:
            self.permissions.append(permission)
            self._mark_updated()

    def revoke_permission(self, permission: str):
        """Remove a permission if it exists."""
        if permission in self.permissions:
            self.permissions.remove(permission)
            self._mark_updated()

    def _mark_updated(self):
        """Update the timestamp whenever modification occurs."""
        self.updated_at = datetime.utcnow()

    def update_staff_patch(self, payload: StaffUpdateRequestSchema | dict, staff_repo) -> dict:
        """
        Partial update (PATCH) — returns a dict of only fields that actually changed.
        Supports both dict or Pydantic model as input.
        `staff_repo` is your repository/data access layer to query existing staff.
        """

        updatable_fields = ["staff_name", "staff_id", "phone_number", "address", "permissions", "role"]
        changed = {}

        # --- uniqueness checks ---
        staff_id_value = payload.get("staff_id") if isinstance(payload, dict) else getattr(payload, "staff_id", None)
        staff_name_value = payload.get("staff_name") if isinstance(payload, dict) else getattr(payload, "staff_name", None)
        phone_value = payload.get("phone_number") if isinstance(payload, dict) else getattr(payload, "phone_number", None)

        if staff_id_value and staff_repo.exists_staff_id(staff_id_value, exclude_id=self.id):
            raise StaffAlreadyExistsAppException("staff_id", staff_id_value)

        if staff_name_value and staff_repo.exists_staff_name(staff_name_value, exclude_id=self.id):
            raise StaffAlreadyExistsAppException("staff_name", staff_name_value)

        if phone_value and staff_repo.exists_phone_number(phone_value, exclude_id=self.id):
            raise StaffAlreadyExistsAppException("phone_number", phone_value)

        # --- apply updates ---
        for field in updatable_fields:
            value = payload.get(field) if isinstance(payload, dict) else getattr(payload, field, None)
            if value is not None:
                current_value = getattr(self, field, None)
                if value != current_value:
                    setattr(self, field, value)
                    changed[field] = value

        if changed:
            self._mark_updated()
        else:
            raise StaffNoChangeAppException("No changes detected for Staff")
        
        return changed

    def soft_delete(self, deleted_by: ObjectId):
        """Mark the staff as deleted without removing from persistence."""
        if self.deleted:
            raise NoChangeAppException("Staff already deleted")
        self.deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by
        self._mark_updated()

    def require_permission(self, permission: str):
        """Ensure staff has the given permission."""
        if self.role == StaffRole.ADMIN:
            return
        if permission not in self.permissions:
            raise StaffPermissionException(f"Permission '{permission}' required")

    # ============================================================
    # Validation
    # ============================================================

    @classmethod
    def validate_role(cls, role: SystemRole | str) -> SystemRole:
        """Ensure role is a valid SystemRole enum."""
        try:
            return role if isinstance(role, SystemRole) else SystemRole(role)
        except ValueError:
            raise InvalidStaffRoleException(f"Invalid role: {role}")


# ============================================================
# Factory
# ============================================================
class StaffFactory:
    """Factory responsible for creating new Staff aggregates."""

    def create_staff(
        self,
        payload: StaffCreateRequestSchema,
        created_by: ObjectId,
        user_id: Optional[ObjectId] = None,
    ) -> Staff:
        return Staff(
            user_id=user_id,
            staff_id=payload.staff_id,
            staff_name=payload.staff_name,
            role=Staff.validate_role(payload.role),
            phone_number=payload.phone_number,
            address=payload.address,
            created_by=created_by,
        )


# ============================================================
# Mapper
# ============================================================
class StaffMapper:
    """Responsible for converting between persistence, domain, and DTO models."""

    @classmethod
    def to_domain(cls, data: dict) -> Staff:
        """Convert MongoDB dict → Domain object."""
        id_value = data.get("_id") or data.get("id") or ObjectId()
        if id_value and not isinstance(id_value, ObjectId):
            id_value = ObjectId(id_value)

        role = Staff.validate_role(data.get("role"))
        return Staff(
            id=id_value,
            user_id=data.get("user_id"),
            staff_id=data.get("staff_id"),
            staff_name=data.get("staff_name"),
            phone_number=data.get("phone_number"),
            address=data.get("address", ""),
            permissions=data.get("permissions", []),
            role=role,
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deleted=data.get("deleted", False),
            deleted_at=data.get("deleted_at"),
            deleted_by=data.get("deleted_by"),
        )

    @classmethod
    def to_persistence_dict(cls, staff: Staff) -> dict:
        """Convert Domain → MongoDB dict (for saving)."""
        return {
            "_id": staff.id or ObjectId(),
            "user_id": staff.user_id,
            "staff_id": staff.staff_id,
            "staff_name": staff.staff_name,
            "phone_number": staff.phone_number,
            "address": staff.address,
            "role": staff.role.value,
            "permissions": staff.permissions,
            "created_by": staff.created_by,
            "created_at": staff.created_at,
            "updated_at": staff.updated_at,
            "deleted_at": staff.deleted_at,
            "deleted": staff.deleted,
            "deleted_by": staff.deleted_by,
        }

    @classmethod
    def to_safe_dict(cls, staff: Staff) -> dict:
        """Convert Domain → Safe dict for JSON/API (stringify IDs)."""
        return {
            "id": str(staff.id) if staff.id else None,
            "user_id": str(staff.user_id) if staff.user_id else None,
            "staff_id": staff.staff_id,
            "staff_name": staff.staff_name,
            "phone_number": staff.phone_number,
            "address": staff.address,
            "role": staff.role.value if isinstance(staff.role, StaffRole) else str(staff.role),
            "permissions": staff.permissions,
            "created_by": str(staff.created_by) if staff.created_by else None,
            "created_at": staff.created_at,
            "updated_at": staff.updated_at,
            "deleted_at": staff.deleted_at,
            "deleted": staff.deleted,
            "deleted_by": str(staff.deleted_by) if staff.deleted_by else None,
        }

    @classmethod
    def to_dto(cls, staff: Staff) -> StaffBaseDataDTO:
        """Convert Domain → DTO (Pydantic)."""
        role_enum = SystemRole(staff.role.value) if isinstance(staff.role, StaffRole) else staff.role
        return StaffBaseDataDTO(
            id=str(staff.id) if staff.id else None,
            user_id=str(staff.user_id) if staff.user_id else None,
            staff_name=staff.staff_name,
            staff_id=staff.staff_id,
            role=role_enum,
            permissions=staff.permissions,
            phone_number=staff.phone_number,
            address=staff.address,
            created_at=staff.created_at,
            created_by=str(staff.created_by) if staff.created_by else None,
            updated_at=staff.updated_at,
            deleted_at=staff.deleted_at,
            deleted=staff.deleted,
            deleted_by=str(staff.deleted_by) if staff.deleted_by else None,
        )