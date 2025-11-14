from pymongo.database import Database
from bson import ObjectId
from typing import List, Tuple, Union, Optional
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.iam.models import IAMFactory , IAMMapper 
from app.contexts.iam.data_transfer.responses import IAMBaseDataDTO
from app.contexts.iam.services import IAMService
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.admin.read_models import AdminReadModel
from app.contexts.admin.data_transfer.requests import (
    AdminCreateUserSchema,
    AdminUpdateUserSchema,
)
from app.contexts.shared.decorators.logging_decorator import log_operation
class UserAdminService:
    def __init__(self, db: Database):
        self.db = db
        self._iam_service: Optional[IAMService] = None
        self._admin_read_model: Optional[AdminReadModel] = None
        self._iam_factory: Optional[IAMFactory] = None
        self.user_collection = self.db["users"]


    def _convert_id(self, id: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_ids(id)

    @property
    def iam_service(self) -> IAMService:
        if self._iam_service is None:
            self._iam_service = IAMService(self.db)
        return self._iam_service
    @property
    def admin_read_model(self) -> AdminReadModel:
        if self._admin_read_model is None:
            self._admin_read_model = AdminReadModel(self.db)
        return self._admin_read_model



        
    @property
    def iam_factory(self) -> IAMFactory:
        if self._iam_factory is None:
            self._iam_factory = IAMFactory(user_read_model=self.admin_read_model.iam_read_model)
        return self._iam_factory

    @log_operation(level="INFO")
    def admin_create_user(self, payload: AdminCreateUserSchema, created_by: str | ObjectId) -> IAMBaseDataDTO:
        payload.created_by = self._convert_id(created_by)
        iam_model = self.iam_factory.create_user(
            email=payload.email,
            password=payload.password,
            username=payload.username,
            role=payload.role,
            created_by=payload.created_by
        )
        iam_model = self.iam_service.save_domain(iam_model)
        return IAMMapper.to_dto(iam_model)


    @log_operation(level="INFO")
    def admin_update_user(
        self, user_id: str | ObjectId, payload: AdminUpdateUserSchema
    ) -> IAMBaseDataDTO:
        return self.iam_service.update_info(self._convert_id(user_id), payload, update_by_admin=True)

    def admin_soft_delete_user(self, user_id: str | ObjectId) -> IAMBaseDataDTO:
        return self.iam_service.soft_delete(self._convert_id(user_id))

    def admin_hard_delete_user(self, user_id: str | ObjectId) -> bool:
        return self.iam_service.hard_delete(self._convert_id(user_id))

    @log_operation(level="INFO")
    def admin_get_users(
        self, role: Union[str, list[str]], page: int, page_size: int
    ) -> Tuple[List[IAMBaseDataDTO], int]:
        cursor, total = self.admin_read_model.get_page_by_role(
            role, page=page, page_size=page_size
        )
        users = mongo_converter.cursor_to_dto(cursor, IAMBaseDataDTO)
        return users, total
