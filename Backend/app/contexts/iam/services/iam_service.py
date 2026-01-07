from __future__ import annotations

from typing import Union, Any

from bson import ObjectId
from pymongo.database import Database

from app.contexts.iam.repositories.iam_repositorie import MongoIAMRepository
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.iam.auth.services import AuthService
from app.contexts.iam.data_transfer.response import IAMResponseDataDTO, IAMBaseDataDTO
from app.contexts.iam.data_transfer.request import IAMUpdateSchema
from pymongo import ReturnDocument
from app.contexts.iam.errors.iam_exception import (
    NotFoundUserException,
    UserDeletedException,
    InvalidPasswordException,
    UserInactiveException,
)

from app.contexts.iam.auth.refresh_utils import (
    create_refresh_token,
    hash_refresh_token,
    now_utc,
    REFRESH_TTL,
)

from app.contexts.iam.auth.password_reset_utils import (
    hash_reset_token
)
from app.contexts.iam.policies.iam_uniqueness_policy import IAMUniquenessPolicy
# NOTE: This assumes your MongoIAMRepository has:
# - update_password(user_id: ObjectId|str, password_hash: str) -> int
# - update(user_id: ObjectId, user: dict) -> IAM
# - find_one(id: ObjectId) -> IAM|None


class IAMService:
    """Identity & Access Management Service"""

    def __init__(self, db: Database):
        self.db = db
        self._iam_repository = MongoIAMRepository(db["iam"])
        self._iam_read_model = IAMReadModel(db)
        self._iam_mapper = IAMMapper()
        self._auth_service = AuthService()
        self._uniqueness_policy = IAMUniquenessPolicy(self._iam_read_model)

        self._refresh_tokens = db["refresh_tokens"]
        self._password_resets = db["password_resets"]

    # -------------------------
    # Internal helpers
    # -------------------------
    def _oid(self, v: str | ObjectId) -> ObjectId:
        return v if isinstance(v, ObjectId) else ObjectId(str(v))

    def _require_active_user(self, user_id: str | ObjectId) -> dict:
        raw_user = self._iam_read_model.get_by_id(str(user_id))
        if not raw_user:
            raise NotFoundUserException(str(user_id))

        iam_model = self._iam_mapper.to_domain(raw_user)
        if iam_model.is_deleted():
            raise UserDeletedException(str(user_id))
        if iam_model.is_inactive():
            raise UserInactiveException(str(user_id))

        return raw_user

    def _revoke_all_refresh_tokens_for_user(self, user_id: str) -> int:
        res = self._refresh_tokens.update_many(
            {"user_id": str(user_id), "revoked_at": None},
            {"$set": {"revoked_at": now_utc()}},
        )
        return int(res.modified_count)

    def _revoke_refresh_token(self, refresh_token: str) -> int:
        rt = str(refresh_token or "").strip()
        if not rt:
            return 0
        rt_hash = hash_refresh_token(rt)
        res = self._refresh_tokens.update_many(
            {"token_hash": rt_hash, "revoked_at": None},
            {"$set": {"revoked_at": now_utc()}},
        )
        return int(res.modified_count)

    # -------------------------
    # Login / Me
    # -------------------------
    def login(self, email: str, password: str) -> Union[IAMResponseDataDTO, tuple]:
        raw_user = self._iam_read_model.get_by_email(email)
        if not raw_user:
            raise NotFoundUserException(email)

        iam_model = self._iam_mapper.to_domain(raw_user)

        if iam_model.is_deleted():
            raise UserDeletedException(email)
        if iam_model.is_inactive():
            raise UserInactiveException(email)

        if not iam_model.check_password(password, self._auth_service):
            raise InvalidPasswordException(password)

        safe_dict = self._iam_mapper.to_safe_dict(iam_model)

        access = self._auth_service.create_access_token(safe_dict)
        refresh = create_refresh_token()

        self._refresh_tokens.insert_one(
            {
                "user_id": str(safe_dict["id"]),
                "token_hash": hash_refresh_token(refresh),
                "created_at": now_utc(),
                "expires_at": now_utc() + REFRESH_TTL,
                "revoked_at": None,
                "replaced_by_hash": None,
            }
        )

        dto = IAMResponseDataDTO(user=IAMBaseDataDTO(**safe_dict), access_token=access)
        return dto, refresh

    def me(self, user_id: str) -> IAMBaseDataDTO:
        raw_user = self._iam_read_model.get_active_by_id(user_id)
        if not raw_user:
            raise NotFoundUserException(user_id)

        iam_model = self._iam_mapper.to_domain(raw_user)
        if iam_model.is_deleted():
            raise UserDeletedException(user_id)
        if iam_model.is_inactive():
            raise UserInactiveException(user_id)

        safe_dict = self._iam_mapper.to_safe_dict(iam_model)
        return IAMBaseDataDTO(**safe_dict)

    # -------------------------
    # Profile update (PATCH /update_info)
    # -------------------------
    def update_info(
        self,
        user_id: ObjectId | str,
        payload: IAMUpdateSchema,
        *,
        update_by_admin: bool = False,
    ):

        user_oid = self._oid(user_id)

        raw_user = self._require_active_user(user_id)
        iam_model = self._iam_mapper.to_domain(raw_user)
        new_username = None
        if payload.username is not None:
            candidate = str(payload.username).strip()
            if candidate != (iam_model.username or ""):
                new_username = candidate if candidate != "" else None

        new_email = None
        if payload.email is not None:
            candidate = str(payload.email).strip().lower()
            if candidate != (iam_model.email or ""):
                new_email = candidate

        if new_username is not None or new_email is not None:
            self._uniqueness_policy.ensure_unique(
                username=new_username,
                email=new_email,
                exclude_user_id=user_oid,
            )

        hashed_pw = None
        if payload.password is not None and str(payload.password).strip() != "":
            if not update_by_admin:
                current_pw = getattr(payload, "current_password", None)
                if not current_pw:
                    raise ValueError("Current password is required to change password")

                if not iam_model.check_password(str(current_pw), self._auth_service):
                    raise InvalidPasswordException("current_password")

            hashed_pw = self._auth_service.hash_password(str(payload.password))

        email_to_set = new_email if new_email is not None else None
        username_to_set = new_username if new_username is not None else None

        iam_model.update_info(
            email=email_to_set,
            username=username_to_set,
            password=hashed_pw if hashed_pw is not None else None,
        )

        self._iam_repository.update(iam_model.id, self._iam_mapper.to_persistence(iam_model))

        if hashed_pw is not None:
            self._revoke_all_refresh_tokens_for_user(str(iam_model.id))

        return iam_model
    # -------------------------
    # Change password (logged-in)
    # POST /change-password
    # -------------------------
    def change_password(self, user_id: ObjectId | str, current_password: str, new_password: str) -> dict:
        user_oid = self._oid(user_id)

        raw_user = self._require_active_user(user_id)
        iam_model = self._iam_mapper.to_domain(raw_user)

        current_password = str(current_password or "")
        new_password = str(new_password or "")

        if not current_password or not new_password:
            raise ValueError("Current password and new password are required")

        if current_password == new_password:
            raise ValueError("New password must be different")

        if not iam_model.check_password(current_password, self._auth_service):
            raise InvalidPasswordException("current_password")

        hashed_pw = self._auth_service.hash_password(new_password)
        modified = self._iam_repository.update_password(iam_model.id, hashed_pw)
        if modified != 1:
            raise ValueError("Password update failed")

        self._revoke_all_refresh_tokens_for_user(str(iam_model.id))
        return {"message": "Password changed"}

    # -------------------------
    # Confirm reset password (token-based)
    # POST /reset-password/confirm
    # -------------------------
    def confirm_password_reset(self, token: str, new_password: str) -> dict:
        token = str(token or "").strip()
        new_password = str(new_password or "")

        if not token:
            raise ValueError("Token is required")
        if not new_password or len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters")

        token_hash = hash_reset_token(token)

        # Atomically claim token (single-use)
        doc = self._password_resets.find_one_and_update(
            {
                "token_hash": token_hash,
                "used_at": None,
                "expires_at": {"$gt": now_utc()},
            },
            {"$set": {"used_at": now_utc()}},
            return_document=ReturnDocument.AFTER,
        )

        if not doc:
            raise ValueError("Invalid or expired token")

        user_id = str(doc["user_id"])

        raw_user = self._require_active_user(user_id)
        iam_model = self._iam_mapper.to_domain(raw_user)

        hashed_pw = self._auth_service.hash_password(new_password)

        modified = self._iam_repository.update_password(iam_model.id, hashed_pw)
        if modified != 1:
            raise ValueError("Password update failed")

        # Force logout everywhere
        self._revoke_all_refresh_tokens_for_user(str(iam_model.id))

        return {"message": "Password reset successful"}

    # -------------------------
    # Logout (optional service helper)
    # POST /logout
    # -------------------------
    def logout(self, refresh_token: str) -> dict:
        self._revoke_refresh_token(refresh_token)
        return {"message": "Logged out"}