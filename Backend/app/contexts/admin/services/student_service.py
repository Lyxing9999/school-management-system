from pymongo.database import Database
from typing import List, Optional
from app.contexts.student.services import StudentService
from app.contexts.admin.data_transfer.request import (
    AdminUpdateInfoStudentSchema,

)
from app.contexts.student.data_transfer.responses import StudentInfoBaseDataDTO
from bson import ObjectId



class StudentAdminService:
    def __init__(self, db: Database):
        self.db = db
        self._student_service: Optional[StudentService] = None
        self.student_collection = self.db["students"]

    def _convert_id(self, id: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_ids(id)

    def admin_get_student_by_user_id(self, user_id: str) -> StudentInfoBaseDataDTO:
        return self.student_service.get_student_info(user_id)

    def admin_update_student_info(self, user_id: str, student_payload: AdminUpdateInfoStudentSchema) -> StudentInfoBaseDataDTO:
        return self.student_service.save_student_info(user_id, student_payload)