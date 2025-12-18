from pymongo.database import Database
from bson import ObjectId
from typing import List

from app.contexts.student.services.student_service import StudentService
from app.contexts.admin.data_transfer.request import AdminUpdateStudentSchema
# import AdminCreateStudentSchema too
from app.contexts.admin.read_models.admin_read_model import AdminReadModel

class StudentAdminService:
    def __init__(self, db: Database):
        self._student_service = StudentService(db)
        self._admin_read_model = AdminReadModel(db)

    def admin_get_student_by_user_id(self, user_id: str | ObjectId):
        return self._student_service.get_student_by_user_id(user_id)

    def admin_create_student_profile(self, payload, user_id: str | ObjectId, created_by: str | ObjectId):
        return self._student_service.create_student_profile(
            payload=payload,
            user_id=user_id,
            created_by=created_by,
        )

    def admin_update_student_profile(self, user_id: str | ObjectId, payload: AdminUpdateStudentSchema):
        return self._student_service.update_student_profile(user_id=user_id, payload=payload)

    
    def admin_list_student_select_options(self) -> List[dict]:
        return self._admin_read_model.admin_list_student_select()
    