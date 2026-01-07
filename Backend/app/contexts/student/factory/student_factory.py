from __future__ import annotations

from datetime import datetime, date as date_type
from bson import ObjectId

from app.contexts.student.domain.student import Student, Gender, StudentStatus
from app.contexts.shared.model_converter import mongo_converter

from ..errors.student_exceptions import (
    StudentUserNotFoundException,
    StudentProfileAlreadyExistsException,
    StudentCodeAlreadyExistsException,
    StudentInvalidObjectIdException,
)


class StudentFactory:
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
        current_class_id: str | ObjectId | None = None,
        phone_number: str | None = None,
        address: dict | None = None,
        guardians: list | None = None,
        photo_url: str | None = None,
        created_by: str | ObjectId | None = None,
        source: str = "STUDENT_FACTORY",
    ) -> Student:
        # -------- Normalize IDs --------
        try:
            user_oid = mongo_converter.convert_to_object_id(user_id)
        except Exception:
            raise StudentInvalidObjectIdException(field="user_id", value=user_id)

        created_by_oid: ObjectId | None = None
        if created_by is not None:
            try:
                created_by_oid = mongo_converter.convert_to_object_id(created_by)
            except Exception:
                raise StudentInvalidObjectIdException(field="created_by", value=created_by)

        class_oid: ObjectId | None = None
        if current_class_id is not None:
            try:
                class_oid = mongo_converter.convert_to_object_id(current_class_id)
            except Exception:
                raise StudentInvalidObjectIdException(field="current_class_id", value=current_class_id)

        # -------- Preconditions --------
        user_doc = self.user_read_model.get_by_id(user_oid)
        if not user_doc:
            raise StudentUserNotFoundException(user_id=user_id)

        existing_profile = self.student_read_model.get_by_user_id(user_oid)
        if existing_profile:
            raise StudentProfileAlreadyExistsException(
                user_id=user_id,
                existing_student_id=existing_profile.get("_id") if isinstance(existing_profile, dict) else None,
            )

        if self.student_read_model.get_by_student_code(student_id_code):
            raise StudentCodeAlreadyExistsException(student_id_code=student_id_code)

        # -------- Audit / History --------
        # Keep history timestamps consistent (UTC)
        now_iso = datetime.utcnow().isoformat()

        history = [
            {
                "event": "STUDENT_CREATED",
                "at": now_iso,
                "meta": {
                    "source": source,
                    "created_by": str(created_by_oid) if created_by_oid else None,
                    "user_id": str(user_oid),
                    "student_id_code": student_id_code,
                    "initial_class_id": str(class_oid) if class_oid else None,
                    "initial_grade_level": int(current_grade_level),
                    "initial_status": StudentStatus.ACTIVE.value,
                },
            }
        ]

        # -------- Create Domain Entity --------
        return Student(
            user_id=user_oid,
            student_id_code=student_id_code,
            first_name_kh=first_name_kh,
            last_name_kh=last_name_kh,
            first_name_en=first_name_en,
            last_name_en=last_name_en,
            gender=gender,
            dob=dob,
            current_grade_level=int(current_grade_level),
            current_class_id=class_oid,
            phone_number=phone_number,
            address=address,
            guardians=guardians,
            photo_url=photo_url,
            status=StudentStatus.ACTIVE,
            history=history,
           
        )