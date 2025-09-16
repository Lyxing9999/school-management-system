from datetime import datetime
from bson import ObjectId
from typing import List
from app.contexts.shared.enum.roles import StaffRole
from app.contexts.staff.models import Staff

class HR(Staff):
    def __init__(
        self,
        staff_id: str,
        staff_name: str,
        phone_number: str,
        created_by: ObjectId,
        role: StaffRole.HR,
        id: ObjectId | None = None,
        permissions: List[str] | None = None,
        address: str | None = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        deleted_at: datetime = None,
        deleted: bool = False,
        deleted_by: ObjectId = None,
    ):
        super().__init__(
            staff_id=staff_id,
            staff_name=staff_name,
            role=StaffRole.HR,
            phone_number=phone_number,
            created_by=created_by,
            id=id,
            permissions=permissions,
            address=address,
            created_at=created_at,
            updated_at=updated_at,
            deleted_at=deleted_at,
            deleted=deleted,
            deleted_by=deleted_by
        )

    def approve_leave(self, staff_id: str):
        pass
    

    @classmethod
    def validate_hr_create_role(cls, role: StaffRole) -> StaffRole:
        forbidden_roles = [StaffRole.ADMIN, StaffRole.HR]
        if role in forbidden_roles:
            raise InvalidStaffRoleException(f"HR cannot create this role: {role}")
        return role
    



    def add_permission(self, permission: str):
        if not StaffRole.ADMIN in self.permissions:
            raise StaffPermissionException(f"HR cannot add permission {permission}")
        self.permissions.append(permission)
        return self

    def remove_permission(self, permission: str):
        if not StaffRole.ADMIN in self.permissions:
            raise StaffPermissionException(f"HR cannot remove permission {permission}")
        self.permissions.remove(permission)
        return self
        

