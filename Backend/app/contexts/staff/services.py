# app/contexts/hr/services/staff_service.py
from pymongo.database import Database
from bson import ObjectId
from datetime import datetime
import logging
from typing import List
from app.contexts.shared.model_converter import converter_utils
from app.contexts.staff.repositories import StaffRepository
from app.contexts.staff.data_transfer.requests import StaffCreateRequestSchema , StaffUpdateRequestSchema
from app.contexts.staff.models import Staff , StaffFactory , StaffMapper
from app.contexts.iam.data_transfer.requests import UserRegisterSchema 
from app.contexts.staff.data_transfer.responses import StaffReadDataDTO
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.infra.database.db import get_db

logger = logging.getLogger(__name__)

class StaffService:
    def __init__(self, db: Database):
        self._staff_repo = StaffRepository(db)
        self._staff_factory = StaffFactory()
        self._staff_mapper = StaffMapper()


    def _log(self, operation: str, staff_id: str | None = None, extra: dict | None = None):
        msg = f"StaffService::{operation}"
        if staff_id:
            msg += f" [staff_id={staff_id}]"
        logger.info(msg, extra=extra or {})



    def _iam_service(self):
        from app.contexts.iam.services import IAMService
        return IAMService(get_db())

    # -------------------------
    # Create Staff
    # -------------------------
    def create_staff(self, payload: StaffCreateRequestSchema,  created_by: ObjectId) -> dict:
        staff_id = None
        user_id = None
        try:
            user_schema = UserRegisterSchema(
                email=payload.email,
                password=payload.password,
                role=payload.role,
                created_by=created_by
            )
            user, token = self._iam_service().register_user(user_schema, trusted_by_admin=True)
            user_id = mongo_converter.convert_to_object_id(user.id)
            staff_model: Staff = self._staff_factory.create_staff(payload, created_by)
            staff_id = self._staff_repo.save(self._staff_mapper.to_persistence_dict(staff_model))
            staff_model.id = staff_id
            return self._staff_mapper.to_safe_dict(staff_model)

        except Exception as e:
            if staff_id:
                self._staff_repo.delete(staff_id)
            if user_id:
                self._iam_service().delete_user(user_id)
            raise e
    # -------------------------
    # Update Staff
    # -------------------------
    def update_staff(self, staff_id: str | ObjectId, payload: StaffUpdateRequestSchema) -> StaffReadDataDTO:
        staff_id_obj = mongo_converter.convert_to_object_id(staff_id)
        update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        self._staff_repo.update(staff_id_obj, update_data)
        updated_doc = self._staff_repo.find_by_id(staff_id_obj)
        self._log("update_staff", staff_id=str(staff_id_obj))
        return mongo_converter.doc_to_dto(updated_doc, StaffReadDataDTO)


    # -------------------------
    # Assign Payroll
    # -------------------------
    def assign_payroll(self, staff_id: str | ObjectId, salary: float, effective_date: datetime):
        staff_id_obj = mongo_converter.convert_to_object_id(staff_id)
        payroll_data = {
            "salary": salary,
            "effective_date": effective_date,
            "updated_at": datetime.utcnow()
        }
        self._staff_repo.update(staff_id_obj, {"$set": payroll_data})
        self._log("assign_payroll", staff_id=str(staff_id_obj), extra={"salary": salary})
        return self._staff_repo.find_by_id(staff_id_obj)