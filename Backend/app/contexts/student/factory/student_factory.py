from __future__ import annotations
from datetime import date as date_type
from bson import ObjectId

from app.contexts.student.domain.student import Student, Gender
from app.contexts.shared.model_converter import mongo_converter


#TODO
# from app.contexts.student.errors import (
#     StudentProfileAlreadyExistsException,
#     StudentCodeAlreadyExistsException,
#     UserNotFoundException
# )

class StudentFactory:
    """
    Factory for creating Student domain objects.
    Ensures uniqueness of Student ID Code and User linkage.
    """

    def __init__(self, student_read_model, user_read_model):
        self.student_read_model = student_read_model
        self.user_read_model = user_read_model

    def create_student(
        self,
        user_id: str | ObjectId,
        student_id_code: str,
        first_name_kh: str,
        last_name_kh: str,
        first_name_en: str,
        last_name_en: str,
        gender: str | Gender,
        dob: date_type,
        current_grade_level: int,
        phone_number: str | None = None,
        address: dict | None = None,
        guardians: list | None = None,
        photo_url: str | None = None,
    ) -> Student:
        
        # 1. Normalize IDs
        user_oid = mongo_converter.convert_to_object_id(user_id)

        # 2. Check if User Exists (Optional, but good for integrity)
        user_doc = self.user_read_model.get_user_by_id(user_oid)
        if not user_doc:
            # raise UserNotFoundException(user_id)
            raise Exception(f"User {user_id} not found")

        # 3. Rule: One User Account = One Student Profile
        existing_profile = self.student_read_model.get_by_user_id(user_oid)
        if existing_profile:
            # raise StudentProfileAlreadyExistsException(user_id)
            raise Exception(f"User {user_id} already has a student profile")

        # 4. Rule: Unique Student ID Code
        if self.student_read_model.get_by_student_code(student_id_code):
            # raise StudentCodeAlreadyExistsException(student_id_code)
            raise Exception(f"Student code {student_id_code} already exists")

        # 5. Create Domain Object
        return Student(
            user_id=user_oid,
            student_id_code=student_id_code,
            first_name_kh=first_name_kh,
            last_name_kh=last_name_kh,
            first_name_en=first_name_en,
            last_name_en=last_name_en,
            gender=gender,
            dob=dob,
            current_grade_level=current_grade_level,
            photo_url=photo_url,
            phone_number=phone_number,
            address=address,
            guardians=guardians,
        )