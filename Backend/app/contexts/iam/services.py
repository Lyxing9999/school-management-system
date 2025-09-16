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
        user_dict = self._user_mapper.to_persistence(user_model)

        user_id = self._user_repository.save(user_dict)
        if not user_id:
            raise UserNotSavedException(user_id)
        raw_user = self._user_read_model.get_by_id(user_id)
        user_model = self._user_mapper.to_domain(raw_user) 
        token = self._auth_service.create_access_token(self._user_mapper.to_safe(user_model))
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
        token = self._auth_service.create_access_token(self._user_mapper.to_safe(user_model))
        self._log("login", user_id=str(user_model.id), extra={"email": email})
        return user_model, token


    def update_profile( self, user_id: str, update_schema: UserUpdateSchema, *, update_by_admin: bool = False ) -> User:
        validated_id: ObjectId = mongo_converter.convert_to_object_id(user_id)

        raw_user: dict = self._user_read_model.get_by_id(validated_id)
        if not raw_user:
            raise NotFoundUserException(user_id)
        user_model: User = self._user_mapper.to_domain(raw_user)
        update_data = update_schema.model_dump(exclude_unset=True)
        if 'password' in update_data:
            update_data['password'] = self._auth_service.hash_password(update_data['password'])
        user_model.update_info(**update_data)
        modified_count: int = self._user_repository.update(validated_id, self._user_mapper.to_persistence(user_model))

        if modified_count == 0:
            raise NoChangeAppException()
        self._log("update_profile", user_id=str(validated_id))

        return user_model


    def delete_user(self, user_id: str) -> User:
        validated_id = mongo_converter.convert_to_object_id(user_id)
        raw_user = self._user_read_model.get_by_id(validated_id)
        if not raw_user:
            raise NotFoundUserException(user_id)
        
        user_model = self._user_mapper.to_domain(raw_user)
        if not user_model.soft_delete():
            raise NoChangeAppException()
        
        modified_count = self._user_repository.update(validated_id, self._user_mapper.to_persistence(user_model))
        if modified_count == 0:
            raise NoChangeAppException()

        self._log("delete_user", user_id=str(validated_id))
        return user_model


