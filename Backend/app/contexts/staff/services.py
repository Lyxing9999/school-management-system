# app/contexts/hr/services/staff_service.py
from bson import ObjectId
import logging
from app.contexts.staff.repositories import StaffRepository
from app.contexts.staff.data_transfer.requests import StaffCreateRequestSchema , StaffUpdateRequestSchema
from app.contexts.staff.models import Staff , StaffFactory , StaffMapper
from app.contexts.staff.error.staff_exceptions import  StaffNotFoundException
from pymongo.database import Database
from app.contexts.shared.model_converter import mongo_converter

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

    def get_to_staff_domain(self, staff_id: str | ObjectId) -> Staff:
        staff_id_obj = mongo_converter.convert_to_object_id(staff_id)
        raw_staff = self._staff_repo.find_by_id(staff_id_obj)
        if not raw_staff:
            raise StaffNotFoundException(staff_id)
        return StaffMapper.to_domain(raw_staff)

    # -------------------------
    # Create Staff
    # -------------------------
    def create_staff(self, payload: StaffCreateRequestSchema,  created_by: ObjectId) -> Staff:
        staff_model: Staff = self._staff_factory.create_staff(payload, created_by)
        staff_id = self._staff_repo.save(self._staff_mapper.to_persistence_dict(staff_model))
        staff_model.id = staff_id
        return staff_model


    def update_staff(self, staff_id: str | ObjectId, payload: StaffUpdateRequestSchema) -> Staff:
        staff_id_obj = mongo_converter.convert_to_object_id(staff_id)
        staff_model = self.get_to_staff_domain(staff_id_obj)
        if staff_model.update_staff(payload):
            self._staff_repo.update(staff_id_obj, self._staff_mapper.to_persistence_dict(staff_model))
        return staff_model


    def soft_staff_delete(self, staff_id: str | ObjectId, deleted_by: ObjectId | str) -> Staff:
        staff_model = self.get_to_staff_domain(staff_id)
        deleted_by_obj = mongo_converter.convert_to_object_id(deleted_by)
        staff_model.soft_delete(deleted_by_obj)

        staff_id_obj = mongo_converter.convert_to_object_id(staff_id)
        modified_count = self._staff_repo.soft_delete(staff_id_obj, deleted_by_obj)
        if modified_count == 0:
            raise NoChangeAppException("Staff already deleted in DB")

        self._log("soft_delete", staff_id=str(staff_id_obj), extra={"deleted_by": str(deleted_by_obj)})
        return staff_model

    def hard_staff_delete(self, staff_id: str | ObjectId) -> bool:
        count = self._staff_repo.delete(mongo_converter.convert_to_object_id(staff_id))
        if count == 0:
            raise StaffNotFoundException(f"Staff {staff_id} not found or already deleted")
        return True



    # -------------------------
    # Assign Payroll
    # -------------------------
    # def assign_payroll(self, staff_id: str | ObjectId, salary: float, effective_date: datetime):
    #     staff_id_obj = mongo_converter.convert_to_object_id(staff_id)
    #     payroll_data = {
    #         "salary": salary,
    #         "effective_date": effective_date,
    #         "updated_at": datetime.utcnow()
    #     }
    #     self._staff_repo.update(staff_id_obj, {"$set": payroll_data})
    #     self._log("assign_payroll", staff_id=str(staff_id_obj), extra={"salary": salary})
    #     return self._staff_repo.find_by_id(staff_id_obj)