from bson import ObjectId
from app.contexts.iam.domain.iam import IAM, IAMStatus
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO
from app.contexts.shared.lifecycle.domain import Lifecycle
from app.contexts.shared.lifecycle.dto import LifecycleDTO


class IAMMapper:
    @staticmethod
    def _to_object_id(value):
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return value
        return ObjectId(value)

    @staticmethod
    def to_domain(data: dict) -> IAM:
        if isinstance(data, IAM):
            return data

        # id
        raw_id = data.get("_id") or data.get("id")
        id_value = IAMMapper._to_object_id(raw_id) or ObjectId()

        # lifecycle (support both nested and legacy flat fields)
        lc_src = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=lc_src.get("created_at") or data.get("created_at"),
            updated_at=lc_src.get("updated_at") or data.get("updated_at"),
            deleted_at=lc_src.get("deleted_at") or data.get("deleted_at"),
            deleted_by=lc_src.get("deleted_by") or data.get("deleted_by"),
        )

        # role (avoid KeyError; let domain validator decide)
        raw_role = data.get("role")
        role = IAM._validate_role(raw_role)

        # status (avoid Enum(None) crash)
        raw_status = data.get("status")
        status = None if raw_status is None else IAMStatus(raw_status)

        created_by = IAMMapper._to_object_id(data.get("created_by"))

        return IAM(
            id=id_value,
            email=data["email"],
            password=data.get("password"),
            role=role,
            username=data.get("username"),
            status=status,
            created_by=created_by,
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
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
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
            "created_by": str(iam.created_by) if iam.created_by else None,
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
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
            created_by=str(iam.created_by) if iam.created_by else None,
            lifecycle=LifecycleDTO(
                created_at=lc.created_at,
                updated_at=lc.updated_at,
                deleted_at=lc.deleted_at,
                deleted_by=lc.deleted_by,
            ),
        )