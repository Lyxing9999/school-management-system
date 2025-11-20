from pymongo.database import Database
from bson import ObjectId
from typing import List, Tuple, Union, Optional
from app.contexts.iam.domain.iam import  IAM
from app.contexts.iam.services.iam_service import IAMService
from app.contexts.iam.factory.iam_factory import IAMFactory
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
from app.contexts.admin.data_transfer.request import (
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
    def admin_create_user(self, payload: AdminCreateUserSchema, created_by: str | ObjectId) -> IAM:
        payload.created_by = created_by
        iam_model = self.iam_factory.create_user(
            email=payload.email,
            password=payload.password,
            username=payload.username,
            role=payload.role,
            created_by=payload.created_by
        )
        return self.iam_service.save_domain(iam_model)



    @log_operation(level="INFO")
    def admin_update_user(self, user_id: str | ObjectId, payload: AdminUpdateUserSchema) -> IAM:
        return self.iam_service.update_info(user_id, payload, update_by_admin=True)

    def admin_soft_delete_user(self, user_id: str | ObjectId) -> IAM:
        return self.iam_service.soft_delete(user_id)

    def admin_hard_delete_user(self, user_id: str | ObjectId) -> bool:
        return self.iam_service.hard_delete(user_id)

    @log_operation(level="INFO")
    def admin_get_users(self, role: Union[str, list[str]], page: int, page_size: int) -> Tuple[List[dict], int]:
        cursor, total = self.admin_read_model.get_page_by_role(
            role, page=page, page_size=page_size
        )
        return cursor, total
