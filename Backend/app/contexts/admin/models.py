from app.contexts.staff.models import Staff
from bson import ObjectId
from typing import List
from app.contexts.shared.enum.roles import StaffRole
from datetime import datetime


class Admin(Staff):
    def __init__(
        self,
        staff_id: str,
        staff_name: str,
        role: StaffRole.ADMIN,
        phone_number: str,
        id: ObjectId | None = None,
        permissions: List[str] | None = None,
        address: str | None = None,
        created_by: ObjectId | None = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        deleted_at: datetime = None,
        deleted: bool = False,
        deleted_by: ObjectId = None
    ):
        super().__init__(
            staff_id=staff_id,
            staff_name=staff_name,
            role=role,
            phone_number=phone_number,
            created_by = created_by,
            id=id or ObjectId(),
            permissions=permissions,
            address=address,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
            deleted_at=deleted_at,
            deleted=deleted,
            deleted_by=deleted_by
        )

    def grant_permission(self, permission: str):
        if permission not in self.permissions:
            self.permissions.append(permission)

    def revoke_permission(self, permission: str):
        if permission in self.permissions:
            self.permissions.remove(permission)
    









class AdminMapper:

    @classmethod
    def to_domain(cls, admin: dict) -> Admin:
        return Admin(
            staff_id=admin.get("staff_id"),                   
            staff_name=admin.get("staff_name", ""),           
            role=admin.get("role", "admin"),                   
            phone_number=admin.get("phone_number", ""),         
            created_by=admin.get("created_by"),                  
            id=admin.get("id"),
            permissions=admin.get("permissions", []),           
            address=admin.get("address", ""),                    
            created_at=admin.get("created_at"),
            updated_at=admin.get("updated_at"),
            deleted_at=admin.get("deleted_at"),
            deleted=admin.get("deleted", False),                 
            deleted_by=admin.get("deleted_by")
        )   




    @classmethod
    def to_safe_dict(cls, admin: Admin) -> dict:
        return {
            "id": str(admin.id) if admin.id else None,
            "staff_id": admin.staff_id,
            "staff_name": admin.staff_name,
            "phone_number": admin.phone_number,
            "address": admin.address,
            "role": admin.role.value,
            "permissions": admin.permissions,
            "created_by": str(admin.created_by) if admin.created_by else None,
            "created_at": admin.created_at,
            "updated_at": admin.updated_at,
            "deleted_at": admin.deleted_at,
            "deleted": admin.deleted,
            "deleted_by": str(admin.deleted_by) if admin.deleted_by else None
        }