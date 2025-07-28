from abc import ABC, abstractmethod
from pymongo.database import Database
from app.utils.objectid import ObjectId
from app.error.exceptions import AppBaseException, ExceptionFactory, InternalServerError, NotFoundError, DatabaseError, ErrorCategory, ErrorSeverity
from app.shared.model_utils import default_model_utils
from app.dtos.users.user_response_dto import UserResponseDTO
from app.dtos.users.user_update_response_dto import UserUpdateResponseDTO
from app.dtos.users.user_login_dto import UserLoginDataDTO, UserLoginResponseDTO
from app.dtos.users.user_register_dto import UserRegisterDataDTO, UserRegisterResponseDTO
from app.schemas.users.user_create_schema import UserCreateSchema  # Make sure to import Schema
from app.schemas.users.user_update_schema import UserUpdateSchema  # Import update schema
from typing import List
from app.repositories.base_repo import MongoBaseRepository
class AdminService(ABC):
    pass

class AdminServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.users_collection_name = "users"
        self.admin_collection_name = "sub_users"
        self.teacher_collection_name = "teacher_users"
        self.student_collection_name = "student_users"

class AdminServiceImpl(AdminService):
    def __init__(self, config: AdminServiceConfig):
        self.config = config
        self.db = config.db
        self.users_collection = self.db[self.config.users_collection_name]
        self.admin_collection = self.db[self.config.admin_collection_name]
        self.teacher_collection = self.db[self.config.teacher_collection_name]
        self.student_collection = self.db[self.config.student_collection_name]
        self.user_repo = MongoBaseRepository(self.config)
        self.utils = default_model_utils

    def get_all_users(self) -> List[UserResponseDTO]:
        users_cursor = self.user_repo.find_all()
        return self.utils.to_response_model_list(users_cursor)

    def get_user_by_id(self, user_id: str) -> UserResponseDTO:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        return self.utils.convert_to_response_model_dto(user)

    def create_user(self, user: UserCreateSchema) -> UserResponseDTO:
        insert_result = self.user_repo.insert_one(user.model_dump())
        created_user = self.user_repo.find_by_id(insert_result)
        if not created_user:
            raise InternalServerError("Failed to fetch created user")
        return self.utils.to_response_model(created_user)

    def update_user(self, user_id: str, user: UserUpdateSchema) -> UserResponseDTO:
        update_result = self.user_repo.update_one(user_id, user.model_dump(exclude_unset=True))
        if update_result.matched_count == 0:
            raise NotFoundError(f"User with id {user_id} not found")
        updated_user = self.user_repo.find_by_id(user_id)
        return self.utils.to_response_model(updated_user)

    