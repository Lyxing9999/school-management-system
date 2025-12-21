from bson import ObjectId
from app.contexts.shared.lifecycle.domain import Lifecycle
from app.contexts.shared.enum.roles import  SystemRole
from app.contexts.staff.domain.staff import Staff
from app.contexts.staff.domain.value_objects import  StaffName, PhoneNumber
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
class StaffMapper:
    """Convert between MongoDB dict <-> Staff domain <-> DTO."""
    @staticmethod
    def _role_value(role) -> str:
        return getattr(role, "value", str(role))
    @classmethod
    def to_domain(cls, data: dict) -> Staff:
        # --- id ---
        id_value = data.get("_id") or data.get("id") or ObjectId()
        if id_value and not isinstance(id_value, ObjectId):
            id_value = ObjectId(id_value)

        # --- role ---
        role = Staff.validate_role(data.get("role"))

        # --- lifecycle (nested) ---
        lc = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=lc.get("created_at") or data.get("created_at"), 
            updated_at=lc.get("updated_at") or data.get("updated_at"),
            deleted_at=lc.get("deleted_at") or data.get("deleted_at"),
            deleted_by=lc.get("deleted_by") or data.get("deleted_by"),
        )

        return Staff(
            id=id_value,
            user_id=data.get("user_id"),
            staff_id=data.get("staff_id"),
            staff_name=StaffName(data.get("staff_name")),
            phone_number=PhoneNumber(data.get("phone_number")),
            address=data.get("address", ""),
            permissions=data.get("permissions", []),
            role=role,
            created_by=data.get("created_by"),
            lifecycle=lifecycle,
        )

    @classmethod
    def to_persistence_dict(cls, staff: Staff) -> dict:
        """Domain -> Mongo dict (store lifecycle nested)."""
        return {
            "_id": staff.id or ObjectId(),
            "user_id": staff.user_id,
            "staff_id": staff.staff_id,
            "staff_name": staff.staff_name.value,
            "phone_number": staff.phone_number.value,
            "address": staff.address,
           "role": getattr(staff.role, "value", str(staff.role)),
            "permissions": staff.permissions,
            "created_by": staff.created_by,
            "lifecycle": {
                "created_at": staff.lifecycle.created_at,
                "updated_at": staff.lifecycle.updated_at,
                "deleted_at": staff.lifecycle.deleted_at,
                "deleted_by": staff.lifecycle.deleted_by,
            },
        }

    @classmethod
    def to_safe_dict(cls, staff: Staff) -> dict:
        """Domain -> JSON-safe dict."""
        return {
            "id": str(staff.id) if staff.id else None,
            "user_id": str(staff.user_id) if staff.user_id else None,
            "staff_id": staff.staff_id,
            "staff_name": staff.staff_name.value,
            "phone_number": staff.phone_number.value,
            "address": staff.address,
            "role": cls._role_value(staff.role),
            "permissions": staff.permissions,
            "created_by": str(staff.created_by) if staff.created_by else None,

            "created_at": staff.lifecycle.created_at,
            "updated_at": staff.lifecycle.updated_at,
            "deleted_at": staff.lifecycle.deleted_at,
            "deleted_by": str(staff.lifecycle.deleted_by) if staff.lifecycle.deleted_by else None,
        }

    @classmethod
    def to_dto(cls, staff: Staff) -> StaffBaseDataDTO:
        role_enum = SystemRole(cls._role_value(staff.role))

        return StaffBaseDataDTO(
            id=str(staff.id) if staff.id else None,
            user_id=str(staff.user_id) if staff.user_id else None,
            staff_name=staff.staff_name.value,
            staff_id=staff.staff_id,
            role=role_enum,
            permissions=staff.permissions,
            phone_number=staff.phone_number.value,
            address=staff.address,

            created_at=staff.lifecycle.created_at,
            created_by=str(staff.created_by) if staff.created_by else None,
            updated_at=staff.lifecycle.updated_at,

            deleted=False if staff.lifecycle.deleted_at is None else True, 
            deleted_at=staff.lifecycle.deleted_at,
            deleted_by=str(staff.lifecycle.deleted_by) if staff.lifecycle.deleted_by else None,
        )