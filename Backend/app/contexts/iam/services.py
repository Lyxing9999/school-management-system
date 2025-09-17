from pymongo.database import Database
from app.contexts.iam.repositories import UserRepository
from app.contexts.iam.data_transfer.requests import UserRegisterSchema, UserLoginSchema, UserUpdateSchema
from app.contexts.iam.data_transfer.responses import UserRegisterDataDTO, UserLoginDataDTO, UserReadDataDTO, UserResponseDataDTO
from bson import ObjectId
from app.contexts.iam.error.user_exceptions import UsernameAlreadyExistsException, EmailAlreadyExistsException, NotFoundUserException, InvalidPasswordException, UnknownRoleException, RoleNotAllowedException, NoChangeAppException , UserDeletedException, UserNotSavedException
from app.contexts.iam.models import User , UserFactory , UserMapper
from app.contexts.shared.enum.roles import UserRole , SystemRole
from app.contexts.iam.read_models import UserReadModel
from app.contexts.auth.services import AuthService
from app.contexts.shared.model_converter import mongo_converter

import logging

logger = logging.getLogger(__name__)

class IAMService:
    """Identity & Access Management Service"""

    def __init__(self, db: Database):
        self.db = db
        self.mongo_converter = mongo_converter
        self._user_repository = UserRepository(db)
        self._user_read_model = UserReadModel(db)
        self._auth_service = AuthService()
        self._user_factory = UserFactory(self._user_read_model, self._auth_service)
        self._user_mapper = UserMapper()



    def get_user_to_domain(self, user_id: str | ObjectId) -> User:
        user_id = mongo_converter.convert_to_object_id(user_id)
        raw_user = self._user_read_model.get_by_id(user_id)
        if not raw_user:
            raise NotFoundUserException(user_id)
        return self._user_mapper.to_domain(raw_user)
    
    
    def to_safe_dict(self, user: User) -> dict:
        return self._user_mapper.to_safe_dict(user)

    # -------------------------
    # Helper methods
    # -------------------------
    def _validate_unique_fields(self, username: str | None, email: str):
        if username and self._user_read_model.get_by_username(username):
            raise UsernameAlreadyExistsException(username)
        if self._user_read_model.get_by_email(email):
            raise EmailAlreadyExistsException(email)

    def _log(self, operation: str, user_id: str | None = None, extra: dict | None = None):
        msg = f"IAMService::{operation}"
        if user_id:
            msg += f" [user_id={user_id}]"
        logger.info(msg, extra=extra or {})

    def register_user(self, schema: UserRegisterSchema, *, trusted_by_admin: bool = False) -> tuple[User, str]:
        role = schema.role or UserRole.STUDENT
        if role not in SystemRole:
            raise UnknownRoleException(role)
        if not trusted_by_admin and role not in (UserRole.STUDENT, UserRole.PARENT):
            raise RoleNotAllowedException(role)
        self._validate_unique_fields(schema.username, schema.email)
        user_model = self._user_factory.create_user(email=schema.email, password=schema.password, username=schema.username, role=role, created_by=schema.created_by)
        user_id = self._user_repository.save(self._user_mapper.to_persistence(user_model))
        if not user_id:
            raise UserNotSavedException(user_id)
        user_model = self.get_user_to_domain(user_id)
        token = self._auth_service.create_access_token(self._user_mapper.to_safe_dict(user_model))
        self._log("register_user", user_id=str(user_id), extra={"email": schema.email, "created_by_admin": trusted_by_admin})

        return user_model, token

    def login_user(self, email: str, password: str) -> tuple[User, str]:
        raw_user = self._user_read_model.get_by_email(email)
        if not raw_user:
            raise NotFoundUserException(email)
        user_model = self._user_mapper.to_domain(raw_user)
        if user_model.is_deleted():
            raise UserDeletedException(email)
        if not user_model.check_password(password, self._auth_service):
            logger.warning("Failed login attempt", extra={"email": email})
            raise InvalidPasswordException(password)
        token = self._auth_service.create_access_token(self._user_mapper.to_safe_dict(user_model))
        self._log("login", user_id=str(user_model.id), extra={"email": email})
        return user_model, token


    def update_profile(self, user_id: str | ObjectId, update_schema: UserUpdateSchema, *, update_by_admin: bool = False) -> User:
        user_model = self.get_user_to_domain(user_id)
        if update_schema.password is not None:
            update_schema.password = self._auth_service.hash_password(update_schema.password)
        user_model.update_info(**update_schema.model_dump(exclude_unset=True))
        modified_count: int = self._user_repository.update(mongo_converter.convert_to_object_id(user_model.id), self._user_mapper.to_persistence(user_model))
        if modified_count == 0:
            raise NoChangeAppException()
        self._log("update_profile", user_id=str(user_id), extra={"update_by_admin": update_by_admin})
        return user_model

    def soft_delete(self, user_id: str | ObjectId, deleted_by: str | ObjectId | None = None) -> User:
        user_model = self.get_user_to_domain(user_id)
        deleted_by_obj = mongo_converter.convert_to_object_id(deleted_by) if deleted_by else None
        user_model.soft_delete(deleted_by_obj)
        modified_count = self._user_repository.soft_delete(mongo_converter.convert_to_object_id(user_model.id), deleted_by_obj)
        if modified_count == 0:
            raise NoChangeAppException("User already deleted in DB")
        self._log("soft_delete", user_id=str(user_id), extra={"deleted_by": str(deleted_by_obj) if deleted_by else None})
        return user_model


    def hard_delete(self, user_id: str | ObjectId) -> bool:
        deleted_count = self._user_repository.hard_delete(mongo_converter.convert_to_object_id(user_id))
        return deleted_count > 0
    