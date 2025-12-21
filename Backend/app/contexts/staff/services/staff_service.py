from bson import ObjectId
from pymongo.database import Database
from typing import List
from bson import ObjectId
from app.contexts.staff.repositories.staff_repositorie import MongoStaffRepository
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
from app.contexts.staff.data_transfer.requests import StaffCreateSchema, StaffUpdateSchema
from app.contexts.staff.domain.staff import Staff
from app.contexts.staff.domain.value_objects import StaffName, PhoneNumber
from app.contexts.staff.errors.staff_exceptions import (
    StaffNotFoundException,
    StaffNoChangeAppException,
)
from app.contexts.staff.mapper.staff_mapper import StaffMapper
from app.contexts.shared.model_converter import mongo_converter


class StaffService:
    def __init__(self, db: Database):
        self._staff_repo = MongoStaffRepository(db["staff"])
        self._staff_read_model = StaffReadModel(db)
        self._staff_mapper = StaffMapper()


    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)


    # -------------------------
    # Domain helpers
    # -------------------------
    def get_to_staff_domain(self, staff_id: str | ObjectId) -> Staff:
        raw_staff = self._staff_read_model.get_by_user_id(self._oid(staff_id))
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
        staff_obj = Staff(
            user_id=self._oid(user_id) if user_id else None,
            staff_id=payload.staff_id,
            staff_name=StaffName(payload.staff_name),
            role=Staff.validate_role(payload.role),
            phone_number=PhoneNumber(payload.phone_number) if payload.phone_number else None,
            address=payload.address or "",
            created_by=self._oid(created_by),
        )
        self._staff_repo.save(staff_obj)
        return staff_obj


    def update_staff(self, staff_id: str | ObjectId, payload: StaffUpdateSchema | dict) -> Staff:
        staff_obj = self.get_to_staff_domain(staff_id)
        staff_obj.update_staff_patch(payload, self._staff_repo)
        modified_count = self._staff_repo.update(staff_obj.id, StaffMapper.to_persistence_dict(staff_obj))
        if modified_count == 0:
            raise StaffNoChangeAppException("Staff already updated in DB")
        return staff_obj

    def soft_staff_delete(self, staff_id: str | ObjectId, deleted_by: str) -> Staff:
        staff_obj = self.get_to_staff_domain(staff_id)
        staff_obj.soft_delete(self._oid(deleted_by))

        modified_count = self._staff_repo.soft_delete(self._oid(staff_id), self._oid(deleted_by))
        if modified_count == 0:
            raise StaffNoChangeAppException("Staff already deleted in DB")

        return staff_obj

    def hard_staff_delete(self, staff_id: str | ObjectId) -> bool:
        count = self._staff_repo.delete(self._oid(staff_id))
        if count == 0:
            raise StaffNotFoundException(f"Staff {staff_id} not found or already deleted")
        return True

