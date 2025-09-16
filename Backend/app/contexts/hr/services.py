
from app.contexts.staff.read_models import StaffReadModel
from app.contexts.hr.data_transfer.requests import HRCreateStaffRequestSchema
from app.contexts.hr.data_transfer.responses import StaffReadDataDTO
from app.contexts.staff.services import StaffService
from app.contexts.iam.read_models import UserReadModel
from app.contexts.shared.enum.roles import StaffRole
from bson import ObjectId
from app.contexts.shared.model_converter import mongo_converter
from pymongo.database import Database
from app.contexts.staff.models import Staff
from app.contexts.hr.models import HR
from app.contexts.iam.data_transfer.responses import UserReadDataDTO
class HRService:
    def __init__(self, db: Database):
        self._staff_read_model = StaffReadModel(db)
        self._staff_service = StaffService(db)
        self._user_read_model = UserReadModel(db)


    def create_employee(self, payload: HRCreateStaffRequestSchema , created_by: str | ObjectId) -> dict:
        staff_dict = self._staff_service.create_staff(payload, created_by= mongo_converter.convert_to_object_id(created_by))
        return staff_dict

        
    def get_employees(self, page: int, page_size: int) -> dict:
        staff_roles = [role.value for role in StaffRole]
        raw_users, total = self._user_read_model.get_page_by_role(
            roles=staff_roles, page=page, page_size=page_size
        )
        users_dto = mongo_converter.cursor_to_dto(raw_users, UserReadDataDTO)

        data = {
            "users": [
                {**u.model_dump(), 
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "updated_at": u.updated_at.isoformat() if u.updated_at else None,
                "deleted_at": u.deleted_at.isoformat() if u.deleted_at else None
                } 
                for u in users_dto
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max((total + page_size - 1) // page_size, 1),
        }
        return data

    def get_employee_details(self, user_id: str | ObjectId) -> StaffReadDataDTO:
        raw_staff = self._staff_read_model.get_staff_by_id(mongo_converter.convert_to_object_id(user_id))
        hr_model = HR.from_dict(raw_staff)
        return StaffReadDataDTO(**hr_model.to_safe_dict())