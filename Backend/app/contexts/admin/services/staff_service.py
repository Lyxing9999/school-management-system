from pymongo.database import Database
from bson import ObjectId
from typing import List, Tuple, Union, Optional
from app.contexts.staff.models import StaffMapper, Staff
from app.contexts.staff.services import StaffService
from app.contexts.shared.enum.roles import SystemRole 
from app.contexts.admin.data_transfer.requests import (
    AdminCreateStaffSchema,
    AdminUpdateStaffSchema,
)
from app.contexts.admin.data_transfer.responses import AdminUpdateStaffDataDTO
from app.contexts.staff.data_transfer.requests  import  StaffCreateSchema
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO

class StaffAdminService:
    def __init__(self, db: Database):
        self.db = db
        self._staff_service: Optional[StaffService] = None
        self._staff_mapper: Optional[StaffMapper] = None
        self.staff_collection = self.db["staff"]
    @property
    def staff_service(self) -> StaffService:
        if self._staff_service is None:
            self._staff_service = StaffService(self.db)
        return self._staff_service
    @property
    def staff_mapper(self) -> StaffMapper:
        if self._staff_mapper is None:
            self._staff_mapper = StaffMapper()
        return self._staff_mapper


    def _convert_id(self, id: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_ids(id)
    def admin_create_staff( self, payload: AdminCreateStaffSchema, created_by: str, user_id: str | ObjectId ) -> StaffBaseDataDTO:
        return self.staff_service.create_staff(payload, created_by, user_id)
    def admin_update_staff( self, user_id: str | ObjectId, payload: AdminUpdateStaffSchema ) -> AdminUpdateStaffDataDTO:
        return self.staff_service.update_staff(user_id, payload)
    def admin_soft_delete_staff(self, staff_id: str | ObjectId, deleted_by: str | ObjectId) -> bool:
        return self.staff_service.soft_staff_delete(staff_id, deleted_by)
    def admin_hard_delete_staff(self, staff_id: str | ObjectId) -> bool:
        return self.staff_service.hard_staff_delete(staff_id)
    def admin_get_staff_by_id(self, staff_id: str) -> StaffBaseDataDTO:
        staff_domain:Staff =  self.staff_service.get_to_staff_domain(staff_id)
        return StaffMapper.to_dto(staff_domain)
