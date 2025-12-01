from pymongo.database import Database
from bson import ObjectId
from typing import List, Tuple, Union, Optional , Dict , Any
from app.contexts.iam.domain.iam import  IAM
from app.contexts.iam.services.iam_service import IAMService
from app.contexts.iam.factory.iam_factory import IAMFactory
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
from app.contexts.admin.data_transfer.request import (
    AdminCreateUserSchema,
    AdminUpdateUserSchema,
)
from app.contexts.shared.decorators.logging_decorator import log_operation
from typing import Final

class UserAdminService:
    def __init__(self, db: Database):
        self.db = db
        self.iam_service: Final[IAMService] = IAMService(db)
        self.admin_read_model: Final[AdminReadModel] = AdminReadModel(db)
        self.iam_factory: Final[IAMFactory] = IAMFactory(
            user_read_model=self.admin_read_model.iam_read_model
        )

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




    def admin_list_student_select(self) -> List[Dict[str, Any]]:
        return self.admin_read_model.admin_list_student_select()


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
