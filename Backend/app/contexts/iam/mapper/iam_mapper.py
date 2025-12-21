from app.contexts.iam.domain.iam import IAM, IAMStatus
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO
from bson import ObjectId

from app.contexts.shared.lifecycle.domain import Lifecycle  


class IAMMapper:
    @staticmethod
    def to_domain(data: dict) -> IAM:
        if isinstance(data, IAM):
            return data

        id_value = data.get("_id") or data.get("id") or ObjectId()
        if id_value and not isinstance(id_value, ObjectId):
            id_value = ObjectId(id_value)

        lifecycle = Lifecycle(
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deleted_at=data.get("deleted_at"),
            deleted_by=data.get("deleted_by"),
        )

        return IAM(
            id=id_value,
            email=data["email"],
            password=data.get("password"),
            role=IAM._validate_role(data["role"]),
            username=data.get("username"),
            status=IAMStatus(data.get("status")),
            created_by=data.get("created_by"),
            lifecycle=lifecycle,
        )
    @staticmethod
    def to_persistence(iam: IAM) -> dict:
        lc = iam.lifecycle
        return {
            "_id": iam.id,
            "email": iam.email,
            "password": iam.password,
            "role": iam.role.value,
            "username": iam.username,
            "status": iam.status.value if iam.status else None,
            "created_by": iam.created_by,
            # lifecycle (top-level in Mongo)
            "created_at": lc.created_at,
            "updated_at": lc.updated_at,
            "deleted_at": lc.deleted_at,
            "deleted_by": lc.deleted_by,
        }
    @staticmethod
    def to_safe_dict(iam: IAM) -> dict:
        lc = iam.lifecycle
        return {
            "id": str(iam.id),
            "email": iam.email,
            "username": iam.username,
            "role": iam.role.value,
            "status": iam.status.value if iam.status else None,
            "created_by": str(iam.created_by),

            # lifecycle
            "created_at": lc.created_at,
            "updated_at": lc.updated_at,
            "deleted_at": lc.deleted_at,
            "deleted_by": lc.deleted_by,
        }

    @staticmethod
    def to_dto(iam: IAM) -> IAMBaseDataDTO:
        lc = iam.lifecycle
        return IAMBaseDataDTO(
            id=str(iam.id),
            email=iam.email,
            username=iam.username,
            role=iam.role.value,
            status=iam.status.value if iam.status else None,
            created_by=str(iam.created_by),
            # lifecycle
            deleted_at=lc.deleted_at,
            created_at=lc.created_at,
            updated_at=lc.updated_at,
            deleted_by=lc.deleted_by,
        )