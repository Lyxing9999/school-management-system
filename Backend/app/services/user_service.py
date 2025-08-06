from app.enum.enums import Role
from app.utils.objectid import ObjectId # type: ignore
from typing import TypeVar, Generic, Type, Any, Union
from werkzeug.security import generate_password_hash  # type: ignore
import logging
from abc import ABC, abstractmethod
from app.error.exceptions import  PydanticValidationError, NotFoundError,  BadRequestError, InternalServerError,  ErrorSeverity, ErrorCategory, DatabaseError, AppTypeError, NotFoundError, handle_exception
from app.utils.date_utils import ensure_date
from app.repositories.user_repository import  UserRepositoryImpl, get_user_repository
from app.shared.model_utils import default_model_utils
from app.dtos.users import UserRegisterDataDTO, UserRegisterResponseDTO, UserLoginDataDTO, UserLoginResponseDTO, UserResponseDataDTO
from app.schemas.users import UserRegisterSchema, UserLoginSchema
from app.auth.jwt_utils import create_access_token
from pymongo.database import Database 
from datetime import timedelta
from werkzeug.security import check_password_hash 
from app.repositories.base_repo import get_base_repository
from app.repositories.base_repo import BaseRepositoryConfig
logger = logging.getLogger(__name__)



T = TypeVar('T')  # Input Schema Type
R = TypeVar('R')  # Output Response DTO Type


class UserServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection = "users"


class UserService(ABC):
    @property
    @abstractmethod
    def user_repo(self) -> UserRepositoryImpl:
        pass

class MongoUserService(UserService, Generic[T, R]):
    def __init__(self, config: UserServiceConfig):
        self.config = config
        self.db = self.config.db
        self.utils = default_model_utils 
        self._user_repo = get_user_repository(config.db)
        config = BaseRepositoryConfig(db=config.db, collection_name=config.collection)
        self._base_repo = get_base_repository(config)
        self._role_collections = {
            Role.TEACHER.value: self.db["teachers"],
            Role.STUDENT.value: self.db["students"],
            Role.ADMIN.value: self.db["admin"]
        }
    def _get_role_collection(self, role: str):
        collection = self._role_collections.get(role)
        if collection is None:
            raise InternalServerError(f"Collection for role '{role}' not found")
        return collection     

    @property
    def user_repo(self) -> UserRepositoryImpl:
        return self._user_repo
      

    def hash_password(self, raw_password: str) -> str:
        return generate_password_hash(raw_password)

    @staticmethod
    def ensure_date(value: Any) -> Any:
        return ensure_date(value)

    @staticmethod
    def _validate_role(role: str) -> Role:
        if role not in [r.value for r in Role]:
            raise BadRequestError(message="Invalid role provided", details={"role": role}, user_message="The specified user role is invalid.", hint=f"The role {role} is invalid. Please choose another.", status_code=400, severity=ErrorSeverity.HIGH, category=ErrorCategory.BAD_REQUEST)
        return Role(role)

    def _validate_field(self, field: str, value: str) -> None:
        results = self._base_repo.find_by_query({field: value}, {"password": 0})
        if results and len(results) > 0:  # <-- Simple existence check
            raise BadRequestError(
                message=f"{field} already exists",
                details={field: value},
                user_message=f"The {value} is already taken. Please choose another.",
                hint=f"The {field} '{value}' is already taken. Please choose another.",
                status_code=400,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE
            )

    def _build_jwt_payload(self, user_dto: UserResponseDataDTO) -> dict:
        return {
            "id": str(user_dto.id),
            "role": user_dto.role,
            "username": user_dto.username,
            "email": user_dto.email,
        }
    def _generate_access_token(self, user_dto: UserResponseDataDTO) -> str:
        return create_access_token(
            data=self._build_jwt_payload(user_dto),
            expire_delta=timedelta(hours=1)
        )

    def _create_role_specific_id(self, _id: ObjectId, role: Union[Role, str]) -> None:
        if isinstance(role, str):
            role = Role(role)
        role_collection = self._get_role_collection(role)
        data = {'user_id': _id}
        logger.info(f"Creating {role} info for user_id: {_id}")
        role_collection.insert_one(data)
    
    def _verify_password(self, password: str, user_password: str) -> bool:
        return check_password_hash(user_password, password)

    def register_user(self, user_schema: UserRegisterSchema) -> UserRegisterResponseDTO:
        if user_schema.password:
            user_schema.password = self.hash_password(user_schema.password)
        data = user_schema.model_dump(by_alias=True)
        data["role"] = Role.STUDENT.value 
        data["role"] = self._validate_role(data["role"]).value
        self._validate_field("username", data["username"])
        if data.get("email"):
            self._validate_field("email", data["email"])
        result = self._base_repo.insert_one(data)
        _id = ObjectId(result)
        self._create_role_specific_id(_id, Role.STUDENT)
        raw_user_data = self._base_repo.find_by_query({"_id": _id}, {"password": 0})
        raw_user_data["_id"] = str(raw_user_data["_id"])
        user_dto = UserResponseDataDTO.model_validate(raw_user_data)
        access_token = self._generate_access_token(user_dto)
        user_register_data_dto = UserRegisterDataDTO(access_token=access_token, user=user_dto)
        return UserRegisterResponseDTO(data=user_register_data_dto, message="User registered successfully", success=True)

    def login_user(self, user_schema: UserLoginSchema) -> UserLoginResponseDTO:
        username = user_schema.username
        password = user_schema.password
        user_data = self._base_repo.find_by_query({"username": username}, {"username": 1, "password": 1, "role": 1, "_id": 1 , "email": 1})
        logger.debug(f"Login attempt for user: {username}")
        if not self._verify_password(password, user_data["password"]):
            raise BadRequestError(
                message="Invalid username or password",
                details={"username": username},
                user_message="The username or password is incorrect.",
                hint="Please check your username and password and try again.",
                status_code=400,
            )
        user_data["_id"] = str(user_data["_id"])
        user_dto = self.utils.convert_to_response_model_dto(user_data, UserResponseDataDTO)
        access_token = self._generate_access_token(user_dto)
        
        login_data_dto = UserLoginDataDTO(
            access_token=access_token,
            user=user_dto
        )
        return UserLoginResponseDTO(
            data=login_data_dto,
            message="Login successful",
            success=True
        )



    def create_user(self, user_schema: T, response_model: Type[R]) -> R:
        if hasattr(user_schema, 'password') and user_schema.password:
            user_schema.password = self.hash_password(user_schema.password)
        data = user_schema.model_dump(by_alias=True)
        username = data.get("username")
        email = data.get("email")
        role = data.get("role") or Role.STUDENT.value
        role = self._validate_role(role).value
        self._validate_field("username", username)
        if email is not None:
            self._validate_field("email", email)
        insert_result = self._base_repo.insert_one(data)
        _id = ObjectId(insert_result)
        self._create_role_specific_id(_id, role)
        raw_user_data = self._base_repo.find_by_query({"_id": _id}, {"password": 0})
        raw_user_data["_id"] = str(raw_user_data["_id"])
        user_dto = self.utils.convert_to_response_model_dto(raw_user_data, response_model)
        return user_dto



    def updated_user(self, user_id: Union[str, ObjectId], update_data: T, response_model: Type[R]) -> R:
        try:
            validated_id = self.utils.validate_object_id(user_id)
            query = {"_id": validated_id}
            update_data_dict = update_data.model_dump(by_alias=True)
            update_count = self._base_repo.update_one(query, update_data_dict)
            if update_count == 0:
                raise NotFoundError(
                    message="User not found",
                    details={"received_value": user_id},
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.SYSTEM,
                    status_code=404,
                    user_message="No changes were made. Please check if the user exists.",
                    hint="Ensure the user ID is correct and exists in the system.",
                )
            raw_user_data = self._base_repo.find_by_query({"_id": validated_id}, {"password": 0})
            raw_user_data["_id"] = str(raw_user_data["_id"])
            return response_model.model_validate(raw_user_data)
        except Exception as e:
            app_exc = handle_exception(e)
            logger.error(f"Unexpected error: {app_exc}")
            raise app_exc

    def delete_user(self, _id: str) -> bool:
        validated_id = self.utils.validate_object_id(_id)
        query = {"_id": validated_id}
        result = self.collection.delete_one(query)
        if result.deleted_count > 0:
            return True




def get_user_service(db: Database) -> MongoUserService:
    return MongoUserService(UserServiceConfig(db))






