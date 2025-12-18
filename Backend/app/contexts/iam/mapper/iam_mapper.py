from app.contexts.iam.domain.iam import IAM
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO
from bson import ObjectId
from app.contexts.shared.lifecycle.types import Status
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
            password=data.get("password"),
            role=IAM._validate_role(data["role"]),
            username=data.get("username"),
            status = Status(data.get("status", "active")),
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
            "status": iam.status.value,
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
            "status": iam.status.value,
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
            status=iam.status.value,
            created_by=str(iam.created_by),
            created_at=iam.created_at,
            updated_at=iam.updated_at,
            deleted=iam.deleted,
            deleted_by=str(iam.deleted_by)
        )