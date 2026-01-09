from __future__ import annotations

from typing import Optional
from urllib.parse import urlencode
from pymongo.database import Database
from bson import ObjectId

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.config.setting import settings
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
from app.contexts.admin.data_transfer.requests import (
    AdminCreateUserSchema,
    AdminUpdateUserSchema,
    AdminSetUserStatusSchema,
)
from app.contexts.iam.auth.services import AuthService

from app.contexts.iam.domain.iam import IAM
from app.contexts.iam.factory.iam_factory import IAMFactory
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.iam.repositories.iam_repositorie import MongoIAMRepository
from app.contexts.iam.policies.iam_uniqueness_policy import IAMUniquenessPolicy
from app.contexts.iam.services.iam_lifecycle_service import IAMLifecycleService
from app.contexts.iam.errors.iam_exception import (
    NotFoundUserException,
    UserDeletedException,
    UserInactiveException,
)
from app.contexts.iam.auth.password_reset_utils import create_reset_token, hash_reset_token, now_utc, RESET_TTL
class UserAdminService:
    """
    Admin-facing orchestration service for IAM users.

    Key invariants enforced here:
    - All IDs are normalized to ObjectId
    - Update only mutates fields that are actually provided
    - Uniqueness policy runs only when username/email is changing
    """

    def __init__(
        self,
        db: Database,
        *,
        iam_repository: MongoIAMRepository | None = None,
        iam_read_model: IAMReadModel | None = None,
        admin_read_model: AdminReadModel | None = None,
        auth_service: AuthService | None = None,
        iam_mapper: IAMMapper | None = None,
        uniqueness_policy: IAMUniquenessPolicy | None = None,
        iam_factory: IAMFactory | None = None,
        iam_lifecycle_service: IAMLifecycleService | None = None,
    ) -> None:
        # Allow DI for tests; default to concrete implementations.
        self.db = db
        self._iam_repository = iam_repository or MongoIAMRepository(self.db["iam"])
        self._iam_read_model = iam_read_model or IAMReadModel(self.db)
        self._admin_read_model = admin_read_model or AdminReadModel(self.db)
        self._auth_service = auth_service or AuthService()
        self._iam_mapper = iam_mapper or IAMMapper()
        self._uniqueness_policy = uniqueness_policy or IAMUniquenessPolicy(self._iam_read_model)
        self._iam_factory = iam_factory or IAMFactory(iam_read_model=self._iam_read_model)
        self._iam_lifecycle_service = iam_lifecycle_service or IAMLifecycleService(self.db)


    def _oid(self, value: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(value)

    def _require_user(self, user_id: str | ObjectId) -> tuple[ObjectId, IAM]:
        user_oid = self._oid(user_id)
        iam = self._iam_repository.find_one(user_oid)
        if not iam:
            raise NotFoundUserException(str(user_id))
        return user_oid, iam

    def admin_create_user(self, payload: AdminCreateUserSchema, created_by: str | ObjectId) -> IAM:
        created_by_oid = self._oid(created_by)

        iam = self._iam_factory.create_user(
            email=payload.email,
            password=payload.password,
            username=payload.username,
            role=payload.role,
            created_by=created_by_oid,
        )
        return self._iam_repository.save(self._iam_mapper.to_persistence(iam))

    def admin_update_user(self, user_id: str | ObjectId, payload: AdminUpdateUserSchema) -> IAM:
        user_oid, iam = self._require_user(user_id)

        new_username = payload.username if payload.username is not None and payload.username != iam.username else None
        new_email = payload.email if payload.email is not None and payload.email != iam.email else None

        if new_username is not None or new_email is not None:
            self._uniqueness_policy.ensure_unique(
                username=new_username,
                email=new_email,
                exclude_user_id=user_oid,
            )

        hashed_password = (
            self._auth_service.hash_password(payload.password)
            if payload.password is not None and payload.password != ""
            else None
        )

        email_to_set = payload.email if payload.email is not None else iam.email
        username_to_set = payload.username if payload.username is not None else iam.username

        iam.update_info(
            email=email_to_set,
            username=username_to_set,
            password=hashed_password,
        )

        return self._iam_repository.update(user_oid, self._iam_mapper.to_persistence(iam))

    def admin_soft_delete_user(self, user_id: str | ObjectId, actor_id: str | ObjectId) -> None:
        user_oid = self._oid(user_id)
        actor_oid = self._oid(actor_id)
        self._iam_lifecycle_service.soft_delete_user(user_oid, actor_oid)

    def admin_restore_user(self, user_id: str | ObjectId, actor_id: str | ObjectId) -> None:
        user_oid = self._oid(user_id)
        actor_oid = self._oid(actor_id)
        self._iam_lifecycle_service.restore_user(user_oid, actor_oid)

    def admin_set_user_status(self, user_id: str | ObjectId, schema: AdminSetUserStatusSchema) -> dict:
        user_oid, iam = self._require_user(user_id)
        iam.set_status(schema.status)
        self._iam_repository.update(user_oid, self._iam_mapper.to_persistence(iam))
        return {"id": str(user_oid), "status": schema.status.value}


    def admin_request_password_reset(self, target_user_id: str, admin_id: str | ObjectId) -> dict:
        raw_user = self._iam_read_model.get_by_id(target_user_id)
        if not raw_user:
            raise NotFoundUserException(target_user_id)

        iam_model = self._iam_mapper.to_domain(raw_user)
        if iam_model.is_deleted():
            raise UserDeletedException(target_user_id)
        if iam_model.is_inactive():
            raise UserInactiveException(target_user_id)

        token = create_reset_token()
        token_hash = hash_reset_token(token)

        resets = self.db["password_resets"]
        resets.insert_one({
            "user_id": str(iam_model.id),
            "token_hash": token_hash,
            "created_by": str(admin_id),
            "created_at": now_utc(),
            "expires_at": now_utc() + RESET_TTL,
            "used_at": None,
        })

        base = (settings.FRONTEND_URL or "").rstrip("/")  
        query = urlencode({"token": token})
        reset_link = f"{base}/auth/reset-password?{query}"

        return {"message": "Password reset created", "reset_link": reset_link}


    def admin_get_users(
        self,
        role: str | list[str],
        page: int,
        page_size: int,
        search: Optional[str] = None,
    ) -> tuple[list[dict], int]:
        rows, total = self._admin_read_model.get_page_by_role(role, page=page, page_size=page_size, search=search)
        if rows is None:
            return [], 0
        if isinstance(rows, list):
            return rows, total
        return list(rows), total

    def admin_hard_delete_user(self, user_id: str | ObjectId, deleted_by: str | ObjectId) -> None:
        user_oid = self._oid(user_id)
        actor_oid = self._oid(deleted_by)
        self._iam_lifecycle_service.hard_delete_user(user_oid, actor_oid)

    def _rollback_purge_user(self, user_id: str | ObjectId) -> None:
        """
        Dangerous internal rollback: direct delete (no lifecycle/policy/audit).
        Keep private and use only for controlled maintenance flows.
        """
        user_oid = self._oid(user_id)
        self._iam_repository.hard_delete(user_oid)