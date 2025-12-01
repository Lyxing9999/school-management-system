from pymongo.database import Database
from bson import ObjectId
from typing import Final
from app.contexts.staff.services import StaffService
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
from app.contexts.admin.data_transfer.request import (
    AdminCreateStaffSchema,
    AdminUpdateStaffSchema,
)
from app.contexts.staff.domain import Staff
class StaffAdminService:
    def __init__(self, db: Database):
        self.db = db
        self._staff_service: Final[StaffService] = StaffService(self.db)
        self._admin_read_model: Final[AdminReadModel] = AdminReadModel(self.db)
    @property
    def staff_service(self) -> StaffService:
        return self._staff_service

    @property
    def admin_read_model(self) -> AdminReadModel:
        return self._admin_read_model

    def admin_create_staff( self, payload: AdminCreateStaffSchema, created_by: str, user_id: str | ObjectId ) -> Staff:
        return self.staff_service.create_staff(payload, created_by, user_id)
    def admin_update_staff( self, user_id: str | ObjectId, payload: AdminUpdateStaffSchema ) -> Staff:
        return self.staff_service.update_staff(user_id, payload)
    def admin_soft_delete_staff(self, staff_id: str | ObjectId, deleted_by: str | ObjectId) -> bool:
        return self.staff_service.soft_staff_delete(staff_id, deleted_by)
    def admin_hard_delete_staff(self, staff_id: str | ObjectId) -> bool:
        return self.staff_service.hard_staff_delete(staff_id)
    def admin_get_staff_by_id(self, staff_id: str) -> Staff:
        return self.staff_service.get_to_staff_domain(staff_id)

    def admin_get_teacher_select(self) -> list[Staff]:
        return self.admin_read_model.admin_list_teacher_select()