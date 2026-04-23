from __future__ import annotations

from typing import Optional
from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.iam.services.user_management_service import UserManagementService
from app.contexts.iam.mapper.iam_mapper import IAMMapper

class HRMSIamGateway:
    """
    HRMS adapter over shared IAM user management.

    HRMS rules live here:
    - restrict allowed roles
    - shape returned summaries for HRMS
    """

    ALLOWED_HRMS_ROLES = {"employee", "manager", "payroll_manager"}

    def __init__(
        self,
        db: Database,
        *,
        user_management_service: UserManagementService | None = None,
        iam_read_model: IAMReadModel | None = None,
        iam_mapper: IAMMapper | None = None
    ) -> None:
        self._user_management = user_management_service or UserManagementService(db)
        self._iam_read_model = iam_read_model or IAMReadModel(db)
        self._iam_mapper = iam_mapper or IAMMapper()

    def _oid(self, value: str | ObjectId | None) -> ObjectId | None:
        if value is None:
            return None
        return mongo_converter.convert_to_object_id(value)

    def _assert_allowed_role(self, role: str) -> str:
        normalized = str(role or "").strip().lower()
        if normalized not in self.ALLOWED_HRMS_ROLES:
            raise ValueError("Role is not allowed in HRMS")
        return normalized

    def _summary_from_raw_user(self, raw_user: dict) -> dict:
        lifecycle = raw_user.get("lifecycle")
        lifecycle = lifecycle if isinstance(lifecycle, dict) else {}

        user_id = str(raw_user.get("_id")) if raw_user.get("_id") is not None else None
        username = raw_user.get("username")
        email = raw_user.get("email")
        deleted_at = raw_user.get("deleted_at") or lifecycle.get("deleted_at")

        return {
            "id": user_id,
            "user_id": user_id,
            "email": email,
            "account_email": email,
            "username": username,
            "account_name": username or email,
            "role": raw_user.get("role"),
            "status": raw_user.get("status"),
            "deleted_at": deleted_at,
            "lifecycle": lifecycle or None,
        }

    # command side
    def create_user_for_employee(
        self,
        *,
        email: str,
        password: str,
        username: str | None = None,
        role: str = "employee",
        created_by: str | ObjectId,
    ):
        allowed_role = self._assert_allowed_role(role)
        return self._user_management.create_user(
            email=email,
            password=password,
            username=username,
            role=allowed_role,
            created_by=created_by,
        )

    def update_user_for_employee(
        self,
        *,
        user_id: str | ObjectId,
        email: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ):
        return self._user_management.update_user(
            user_id=user_id,
            email=email,
            username=username,
            password=password,
        )

    def soft_delete_user(self, *, user_id: str | ObjectId, actor_id: str | ObjectId) -> None:
        self._user_management.soft_delete_user(user_id=user_id, actor_id=actor_id)

    def restore_user(self, *, user_id: str | ObjectId, actor_id: str | ObjectId) -> None:
        self._user_management.restore_user(user_id=user_id, actor_id=actor_id)

    def request_password_reset(self, *, user_id: str | ObjectId, actor_id: str | ObjectId) -> dict:
        return self._user_management.request_password_reset(
            target_user_id=user_id,
            actor_id=actor_id,
        )

    def change_password(self, *, user_id: str | ObjectId, new_password: str) -> None:
        self._user_management.change_password(
            user_id=user_id,
            new_password=new_password,
        )

    # query side
    def get_account_summary_by_user_id(self, user_id: str | ObjectId | None) -> Optional[dict]:
        oid = self._oid(user_id)
        if not oid:
            return None

        raw_user = self._iam_read_model.get_by_id(oid)
        if not raw_user:
            return None

        return self._summary_from_raw_user(raw_user)

    def get_account_summaries_by_user_ids(self, user_ids: list[str | ObjectId]) -> dict[str, dict]:
        oids: list[ObjectId] = []
        for user_id in user_ids:
            oid = self._oid(user_id)
            if oid:
                oids.append(oid)

        if not oids:
            return {}

        raw_users = self._iam_read_model.list_by_ids(oids)

        result: dict[str, dict] = {}
        for raw_user in raw_users:
            result[str(raw_user.get("_id"))] = self._summary_from_raw_user(raw_user)

        return result
    
    def set_user_status(self, *, user_id: str | ObjectId, status: str) -> dict:
        return self._user_management.set_user_status(
            user_id=user_id,
            status=status,
        )
    def get_employee_accounts_page(
        self,
        *,
        page: int = 1,
        page_size: int = 10,
        search: str | None = None,
        show_deleted: str = "active",
        status: str | None = None,
    ):
        rows, total = self._user_management.get_users_by_role(
            role=["employee", "manager", "payroll_manager"],
            page=page,
            page_size=page_size,
            search=search,
            show_deleted=show_deleted,
            status=status,
        )
        return [self._summary_from_raw_user(row) for row in rows], total
        


    def to_account_dto(self, iam):
        return self._iam_mapper.to_dto(iam)
