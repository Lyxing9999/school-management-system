from app.schemas.users.user_create_schema import UserCreateSchema
from app.enum.enums import Role
from app.utils.objectid import ObjectId # type: ignore
from typing import TypedDict, Any, Union
from werkzeug.security import generate_password_hash  # type: ignore
import logging
from abc import ABC, abstractmethod
from app.error.exceptions import  PydanticValidationError, NotFoundError,  BadRequestError, InternalServerError,  ErrorSeverity, ErrorCategory, DatabaseError, AppTypeError, NotFoundError
from app.utils.date_utils import ensure_date
from app.repositories.user_repository import  UserRepositoryImpl, get_user_repository
from app.shared.model_utils import default_model_utils
from app.dtos.users.user_response_dto import UserResponseDTO
from app.dtos.users.user_register_dto import UserRegisterDataDTO , UserRegisterResponseDTO 
from app.dtos.users.user_login_dto import UserLoginDataDTO , UserLoginResponseDTO
from app.schemas.users.user_create_schema import UserCreateSchema
from app.schemas.users.user_login_schema import UserLoginSchema
from app.auth.jwt_utils import create_access_token
from pymongo.database import Database 
from datetime import timedelta
from werkzeug.security import check_password_hash 
from app.dtos.users.user_update_response_dto   import UserUpdateResponseDataDTO, UserUpdateResponseDTO
from app.schemas.users.user_update_schema import UserUpdateSchema
logger = logging.getLogger(__name__)

class UpdateRoleInfoResponse(TypedDict):
    role: str
    update_data: dict
    original_data: dict



class UserServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "users"




class UserService(ABC):
    @property
    @abstractmethod
    def user_repo(self) -> UserRepositoryImpl:
        pass

class MongoUserService(UserService):
    def __init__(self, config: UserServiceConfig):
        self.config = config
        self.db = self.config.db
        self.collection = self.db[self.config.collection_name]
        self.utils = default_model_utils
        self._user_repo = get_user_repository(self.db)
        self._role_collections = {
            Role.TEACHER.value: self.db["teachers"],
            Role.STUDENT.value: self.db["students"],
            Role.ADMIN.value: self.db["users"]
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
        if self.collection.find_one({field: value}):
            raise BadRequestError(message=f"{field} already exists", details={field: value}, user_message=f"The {field} is already taken. Please choose another.", hint=f"The {field} {value} is already taken. Please choose another.", status_code=400, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE)


    def _build_jwt_payload(self, user_dto: UserResponseDTO) -> dict:
        return {
            "id": str(user_dto.id),
            "role": user_dto.role,
            "username": user_dto.username,
            "email": user_dto.email,
        }
    def _generate_access_token(self, user_dto: UserResponseDTO) -> str:
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
    
    def register_user(self, user_schema: UserCreateSchema) -> UserRegisterResponseDTO:
        user_dto =  self.create_user(user_schema)
        if not user_dto:
            raise InternalServerError(
                message="Failed to create user",
                details={"user_schema": user_schema},
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE
            )
        access_token = self._generate_access_token(user_dto)
        user_register_data_dto = UserRegisterDataDTO(access_token=access_token)
        return UserRegisterResponseDTO(data=user_register_data_dto, message="User registered successfully", success=True)

        

    def create_user(self, user_schema: UserCreateSchema) -> UserResponseDTO:  
        if user_schema.password:
            user_schema.password = self.hash_password(user_schema.password)
        data = user_schema.model_dump(by_alias=True)
        username = data.get("username")
        email = data.get("email")
        role = data.get("role", Role.STUDENT.value)
        role = self._validate_role(role)
        self._validate_field("username", username)
        if email is not None:
            self._validate_field("email", email)
        result = self.collection.insert_one(data)
        if not result.acknowledged:
            raise DatabaseError(
                message="Failed to create user in database",
                details={"data": data},
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE
            )
        _id = result.inserted_id
        self._create_role_specific_id(_id, role)
        logger.info(f"User created with id: {_id}, {self.collection}, {data}")
        raw_user_data = self.collection.find_one({"_id": _id})
        if raw_user_data is None:
            raise NotFoundError(message="User not found", details={"_id": _id}, user_message="The user with the given id was not found.", hint="The user with the given id was not found. Please try again later.", status_code=404, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE)
        raw_user_data.pop("password", None)
        raw_user_data["_id"] = str(raw_user_data["_id"])
        user_dto = UserResponseDTO.model_validate(raw_user_data)
        return user_dto


    def login_user(self, user_schema: UserLoginSchema) -> UserLoginResponseDTO:

        username = user_schema.username
        password = user_schema.password
        user_db_dto = self.user_repo.find_user_by_username(username)
        logger.info(f"User DB DTO: {user_db_dto}")

        if not check_password_hash(user_db_dto.password, password): 
            raise BadRequestError(
                message="Invalid username or password",
                details={"username": username},
                user_message="The username or password is incorrect.",
                status_code=400
            )
        user_dto = UserResponseDTO.model_validate(user_db_dto.model_dump(exclude={"password"}, by_alias=True))
        access_token = self._generate_access_token(user_dto)
        user_login_data_dto = UserLoginDataDTO(
            access_token=access_token,
            user=user_dto
        )
        return UserLoginResponseDTO(
            data=user_login_data_dto,
            message="Login successful",
            success=True
        )




    def updated_user(self,user_id: Union[str, ObjectId], update_data: UserUpdateSchema) -> UserUpdateResponseDTO:
        try:
            validated_id = self.utils.validate_object_id(user_id)
            query = {"_id": validated_id}
            update_data_dict = update_data.model_dump(by_alias=True)
            self.user_repo.update_data(query, update_data_dict)
            return UserUpdateResponseDTO(message="User updated successfully", success=True, data=UserUpdateResponseDataDTO(username=update_data_dict.get("username"), email=update_data_dict.get("email")))
        except PydanticValidationError as e:
            raise e




    def delete_user(self, _id: str) -> bool:
        validated_id = self.utils.validate_object_id(_id)
        query = {"_id": validated_id}
        result = self.collection.delete_one(query)
        if result.deleted_count > 0:
            return True
        raise InternalServerError(
            message="User deletion failed; no documents deleted.",
            details={"_id": _id},
            user_message="Could not delete the user. Please try again later."
        )



def get_user_service(db: Database) -> MongoUserService:
    return MongoUserService(UserServiceConfig(db))






