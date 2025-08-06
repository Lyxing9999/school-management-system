from abc import ABC
from pymongo.database import Database
from app.utils.pyobjectid import PyObjectId
from app.schemas.classes import AdminClassCreateSchema
from app.schemas.users import AdminUpdateUserSchema, AdminCreateUserSchema
from app.repositories.base_repo import get_base_repository , BaseRepositoryConfig
from app.dtos.users import AdminCreateUserResponseDTO, AdminFindUserDataDTO, AdminCreateUserDataDTO, AdminUpdateUserDataDTO, AdminUpdateUserResponseDTO, AdminDeleteUserResponseDTO , AdminFindUserResponseDTOList
from app.dtos.classes import AdminClassCreateResponseDTO, AdminClassCreateDataDTO
from app.shared.model_utils import default_model_utils
class AdminService(ABC):
    pass

class AdminServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.users_collection_name = "users" 
    def __repr__(self):
        return f"AdminServiceConfig(db={self.db}, users_collection_name='{self.users_collection_name}')"


class MongoAdminService(AdminService):
    def __init__(self, config: AdminServiceConfig):
        self.config = config
        repo_config = BaseRepositoryConfig(
            db=config.db,
            collection_name=config.users_collection_name  
        )
        self._base_repo = get_base_repository(repo_config)
        self.utils = default_model_utils
        self._user_service = None
        self._class_service = None

    @property
    def user_service(self):
        if self._user_service is None:
            from app.services.user_service import get_user_service
            self._user_service = get_user_service(self.config.db)
        return self._user_service
        

    @property
    def class_service(self):
        if self._class_service is None:
            from app.services.class_service import get_class_service
            self._class_service = get_class_service(self.config.db)
        return self._class_service


    def find_all_users(self) -> AdminFindUserResponseDTOList:
        users_cursor = self._base_repo.find_all()  
        sanitized_users = []
        for user_doc in users_cursor:
            if isinstance(user_doc, dict):
                user_doc = user_doc.copy() 
                user_doc.pop("password", None) 
            sanitized_users.append(user_doc)
        
        user_dto_list = self.utils.convert_to_response_model_list_dto(sanitized_users, AdminFindUserDataDTO)
        
        response_dto_list = AdminFindUserResponseDTOList(
            data=user_dto_list,
            message="Users fetched successfully",
            success=True
        )
        return response_dto_list

    def admin_create_user(self, user_schema: AdminCreateUserSchema) -> AdminCreateUserResponseDTO:
        admin_create_user_data_dto = self.user_service.create_user(user_schema, AdminCreateUserDataDTO)
        response_dto = AdminCreateUserResponseDTO(data=admin_create_user_data_dto, message="User created successfully", success=True)
        return response_dto

    def admin_update_user(self, user_id: str, user_schema: AdminUpdateUserSchema) -> AdminUpdateUserResponseDTO:
        admin_update_user_data_dto = self.user_service.updated_user(user_id, user_schema, AdminUpdateUserDataDTO)
        response_dto = AdminUpdateUserResponseDTO(data=admin_update_user_data_dto, message="User updated successfully", success=True)
        return response_dto

    def admin_delete_user(self, user_id: str) -> AdminDeleteUserResponseDTO:
        admin_delete_user_data_dto = self.user_service.delete_user(user_id, AdminDeleteUserDataDTO)
        response_dto = AdminDeleteUserResponseDTO(data=admin_delete_user_data_dto, message="User deleted successfully", success=True)
        return response_dto
        

    def admin_create_class(self, admin_create_class_schema: AdminClassCreateSchema, admin_id: PyObjectId) -> AdminClassCreateResponseDTO:
        data_dict = admin_create_class_schema.model_dump()
        data_dict["created_by_admin_id"] = admin_id
        class_create_model = self.utils.to_model(data_dict, AdminClassCreateSchema)
        admin_create_class_data_dto = self.class_service.create_class(class_create_model, AdminClassCreateDataDTO)
        response_dto = AdminClassCreateResponseDTO(
            data=admin_create_class_data_dto,
            message="Class created successfully",
            success=True
        )
        return response_dto


def get_admin_service(db: Database) -> MongoAdminService:
    return MongoAdminService(AdminServiceConfig(db))

