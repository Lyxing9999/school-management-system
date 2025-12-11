from pymongo.database import Database
from typing import Dict, Any
from bson import ObjectId
from datetime import datetime
from app.contexts.student.repositories.student_repository import MongoStudentRepository
from app.contexts.student.domain.student import Student, Gender
from app.contexts.shared.model_converter import mongo_converter

class StudentAdminService:
    def __init__(self, db: Database):
 
        self._student_repo = MongoStudentRepository(db['students'])

    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def create_student_profile(self, payload: Any, user_id: ObjectId) -> Student:
        

        if self._student_repo.find_by_user_id(user_id):
            raise Exception("Student profile already exists for this User ID")

        
        dob = payload.dob
        if isinstance(dob, str):
            dob = datetime.strptime(dob, "%Y-%m-%d").date()

        # 3. Create Entity
        student = Student(
            user_id=user_id,
            student_id_code=payload.student_id_code,
            first_name_kh=payload.first_name_kh,
            last_name_kh=payload.last_name_kh,
            first_name_en=payload.first_name_en,
            last_name_en=payload.last_name_en,
            gender=payload.gender,
            dob=dob,
            current_grade_level=payload.current_grade_level,
            # Add other fields...
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        return self._student_repo.insert(student)