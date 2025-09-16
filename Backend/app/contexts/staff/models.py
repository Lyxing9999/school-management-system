# app/contexts/hr/models/staff.py
from datetime import datetime
from bson import ObjectId
from typing import List
from app.contexts.shared.enum.roles import StaffRole
from app.contexts.core.policy.policy_service import PolicyService
from app.contexts.staff.error.staff_exceptions import InvalidStaffRoleException
from app.contexts.staff.data_transfer.requests import StaffCreateRequestSchema

# -------------------------
# Aggregate
# -------------------------
class Staff:
    _policy_service = PolicyService(config_path="app/contexts/core/policy/config/policies.json")

    def __init__(
        self,
        staff_id: str,
        staff_name: str,     
        role: StaffRole,
        phone_number: str,
        created_by: ObjectId,
        id: ObjectId | None = None,
        permissions: List[str] | None = None,
        address: str | None = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        deleted_at: datetime = None,
        deleted: bool = False,
        deleted_by: ObjectId = None
    ):
        self.staff_id = staff_id
        self.role = role
        self.staff_name = staff_name
        self.phone_number = phone_number
        self.created_by = created_by
        self.id = id or ObjectId()
        self.address = address or ""
        self.permissions = permissions if permissions is not None else self._policy_service.get_default_permissions(role)
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
        self.deleted = deleted
        self.deleted_by = deleted_by


    def grant_permission(self, permission: str):
        if permission not in self.permissions:
            self.permissions.append(permission)

    def revoke_permission(self, permission: str):
        if permission in self.permissions:
            self.permissions.remove(permission)

    def soft_delete(self, deleted_by: ObjectId):
        self.deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by


    def require_permission(self, permission: str):
        if self.role == StaffRole.ADMIN:
            return
        if permission not in self.permissions:
            raise StaffPermissionException(f"Permission {permission} required")
    

    @classmethod
    def validate_role(cls, role: StaffRole | str) -> StaffRole:
        try:
            return role if isinstance(role, StaffRole) else StaffRole(role)
        except ValueError:
            raise InvalidStaffRoleException(f"Invalid role: {role}")
    

# -------------------------
# Factory
# -------------------------
class StaffFactory:
    def create_staff(self, payload: StaffCreateRequestSchema, created_by: ObjectId) -> Staff:
        return Staff(
            staff_id=payload.staff_id,
            staff_name=payload.staff_name,
            role=Staff.validate_role(payload.role),
            phone_number=payload.phone_number,
            address=payload.address,
            created_by=created_by
        )

# -------------------------
# Mapper
# -------------------------
class StaffMapper:
    @classmethod
    def create_from_payload(cls, payload, id: ObjectId, created_by: ObjectId) -> "Staff":
        return cls(
            id=id,  
            staff_id=payload.staff_id,
            staff_name=payload.staff_name,
            phone_number=payload.phone_number,
            address=payload.address,
            role=cls.validate_role(payload.role),
            created_by=created_by
        )
    @classmethod
    def to_domain(cls, data: dict) -> Staff:
        id_value = data.get("_id") or data.get("id") or ObjectId()
        if id_value and not isinstance(id_value, ObjectId):
            id_value = ObjectId(id_value)

        role = cls.validate_role(data.get("role"))
        return Staff(
            id=id_value,
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
            deleted_by=data.get("deleted_by")
        )
    @classmethod
    def to_persistence_dict(cls, staff: Staff) -> dict:
        return {
            "_id": staff.id or ObjectId(),
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
            "deleted_by": staff.deleted_by
        }   

    @classmethod
    def to_safe_dict(cls, staff: Staff) -> dict:
        return {
            "id": str(staff.id) if staff.id else None,
            "staff_id": staff.staff_id,
            "staff_name": staff.staff_name,
            "phone_number": staff.phone_number,
            "address": staff.address,
            "role": staff.role.value,
            "permissions": staff.permissions,
            "created_by": str(staff.created_by) if staff.created_by else None,
            "created_at": staff.created_at,
            "updated_at": staff.updated_at,
            "deleted_at": staff.deleted_at,
            "deleted": staff.deleted,
            "deleted_by": str(staff.deleted_by) if staff.deleted_by else None
        }

