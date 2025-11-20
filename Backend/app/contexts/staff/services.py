# app/contexts/hr/services/staff_service.py
from bson import ObjectId
import logging
from pymongo.database import Database
from typing import List
from app.contexts.staff.repositories import StaffRepository
from app.contexts.staff.read_models import StaffReadModel
from app.contexts.staff.data_transfer.requests import StaffCreateSchema, StaffUpdateSchema
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from app.contexts.staff.models import Staff, StaffFactory, StaffMapper
from app.contexts.staff.error.staff_exceptions import (
    StaffNotFoundException,
    StaffNoChangeAppException,
    StaffPermissionException
)
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.log.log_service import LogService

logger = logging.getLogger(__name__)


class StaffService:
    def __init__(self, db: Database):
        self._staff_repo = StaffRepository(db)
        self._staff_read_model = StaffReadModel(db)
        self._staff_factory = StaffFactory()
        self._staff_mapper = StaffMapper()
        self._log_service = LogService.get_instance()

    def _log(self, operation: str, staff_id: str | None = None, extra: dict | None = None, level: str = "INFO"):
        msg = f"StaffService::{operation}" + (f" [staff_id={staff_id}]" if staff_id else "")  # construct message
        self._log_service.log(msg, level=level, module="StaffService", user_id=staff_id, extra=extra or {})  # send to logger

    def convert_id(self, id: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id)


    # -------------------------
    # Domain helpers
    # -------------------------
    def get_to_staff_domain(self, staff_id: str | ObjectId) -> Staff:
        raw_staff = self._staff_read_model.get_staff_by_id(self.convert_id(staff_id))
        if not raw_staff:
            raise StaffNotFoundException(staff_id)
        return StaffMapper.to_domain(raw_staff)

    def get_all_staff_domains(self) -> List[Staff]:
        raw_staff_list = self._staff_read_model.get_all_staff()
        return [StaffMapper.to_domain(s) for s in raw_staff_list]

    # -------------------------
    # CRUD operations
    # -------------------------
    def create_staff(self, payload: StaffCreateSchema, created_by: str, user_id: str | None = None) -> Staff:
        staff_obj = self._staff_factory.create_staff(payload, self.convert_id(created_by), self.convert_id(user_id))
        self._staff_repo.save(StaffMapper.to_persistence_dict(staff_obj))
        self._log("create_staff", staff_id=staff_obj.staff_id, extra={"created_by": str(created_by)})
        return staff_obj


    def update_staff(self, staff_id: str | ObjectId, payload: StaffUpdateSchema | dict) -> Staff:
        staff_obj = self.get_to_staff_domain(staff_id)
        staff_obj.update_staff_patch(payload, self._staff_repo)
        self._staff_repo.update(staff_obj.id, StaffMapper.to_persistence_dict(staff_obj))
        return staff_obj

    def soft_staff_delete(self, staff_id: str | ObjectId, deleted_by: str) -> Staff:
        staff_obj = self.get_to_staff_domain(staff_id)
        staff_obj.soft_delete(self.convert_id(deleted_by))

        modified_count = self._staff_repo.soft_delete(staff_id, self.convert_id(deleted_by))
        if modified_count == 0:
            raise StaffNoChangeAppException("Staff already deleted in DB")

        self._log("soft_delete", staff_id=str(staff_obj.id), extra={"deleted_by": str(deleted_by)})
        return staff_obj

    def hard_staff_delete(self, staff_id: str | ObjectId) -> bool:
        count = self._staff_repo.delete(self.convert_id(staff_id))
        if count == 0:
            raise StaffNotFoundException(f"Staff {staff_id} not found or already deleted")
        self._log("hard_delete", staff_id=str(staff_id))
        return True

    # -------------------------
    # Permission management
    # -------------------------
    def grant_permission(self, staff_id: str | ObjectId, permission: str) -> Staff:
        staff_obj = self.get_to_staff_domain(staff_id)
        staff_obj.grant_permission(permission)
        self._staff_repo.update(staff_obj.id, StaffMapper.to_persistence_dict(staff_obj))
        self._log("grant_permission", staff_id=str(staff_obj.id), extra={"permission": permission})
        return staff_obj

    def revoke_permission(self, staff_id: str | ObjectId, permission: str) -> Staff:
        staff_obj = self.get_to_staff_domain(staff_id)
        staff_obj.revoke_permission(permission)
        self._staff_repo.update(staff_obj.id, StaffMapper.to_persistence_dict(staff_obj))
        self._log("revoke_permission", staff_id=str(staff_obj.id), extra={"permission": permission})
        return staff_obj

    def check_permission(self, staff_id: str | ObjectId, permission: str):
        staff_obj = self.get_to_staff_domain(staff_id)
        try:
            staff_obj.require_permission(permission)
        except StaffPermissionException as e:
            self._log("permission_denied", staff_id=str(staff_obj.id), extra={"permission": permission})
            raise

    # -------------------------
    # Staff name select
    # -------------------------
    def get_staff_name_select(self, search_text: str = "", role: str = "teacher") -> list[dict]:
        return self._staff_read_model.get_staff_name_select(search_text, role)