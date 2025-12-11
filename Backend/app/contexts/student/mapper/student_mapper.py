from __future__ import annotations
from datetime import datetime, date as date_type, time
from typing import Any, Dict


from app.contexts.student.data_transfer.responses import StudentBaseDataDTO
from app.contexts.student.domain.student import Student, Gender, StudentStatus

class StudentMapper:
    """
    Handles conversion between Student domain model, MongoDB dict, and DTOs.
    """

    @staticmethod
    def to_domain(data: Dict[str, Any]) -> Student:
        if not data:
            return None
        
        # Handle Date of Birth
        raw_dob = data.get("dob")
        if isinstance(raw_dob, datetime):
            dob = raw_dob.date()
        elif isinstance(raw_dob, str):
            dob = datetime.fromisoformat(raw_dob).date()
        else:
            dob = raw_dob 

        # Handle Enums
        try:
            gender = Gender(data.get("gender"))
        except ValueError:
            gender = Gender.MALE 

        try:
            status = StudentStatus(data.get("status"))
        except ValueError:
            status = StudentStatus.ACTIVE

        return Student(
            id=data.get("_id"),
            user_id=data["user_id"],
            student_id_code=data["student_id_code"],
            first_name_kh=data["first_name_kh"],
            last_name_kh=data["last_name_kh"],
            first_name_en=data["first_name_en"],
            last_name_en=data["last_name_en"],
            gender=gender,
            dob=dob,
            current_grade_level=data["current_grade_level"],
            photo_url=data.get("photo_url"),
            phone_number=data.get("phone_number"),
            address=data.get("address", {}),
            guardians=data.get("guardians", []),
            status=status,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def to_persistence(student: Student) -> Dict[str, Any]:
        """
        Convert domain entity to MongoDB document.
        """
        dob_dt = None
        if student.dob:
            dob_dt = datetime.combine(student.dob, time.min)

        return {
            "_id": student.id,
            "user_id": student.user_id,
            "student_id_code": student.student_id_code,
            "first_name_kh": student.first_name_kh,
            "last_name_kh": student.last_name_kh,
            "first_name_en": student.first_name_en,
            "last_name_en": student.last_name_en,
            "gender": student.gender.value,
            "dob": dob_dt,
            "current_grade_level": student.current_grade_level,
            "photo_url": student.photo_url,
            "phone_number": student.phone_number,
            "address": student.address,
            "guardians": student.guardians,
            "status": student.status.value,
            "created_at": student.created_at,
            "updated_at": student.updated_at
        }


    @staticmethod
    def to_dto(student: Student) -> StudentBaseDataDTO:
        """
        Convert Domain Entity to Response DTO.
        """
        if not student:
            return None

        return StudentBaseDataDTO(
            id=str(student.id),         
            user_id=str(student.user_id), 
            student_id_code=student.student_id_code,
            
            first_name_kh=student.first_name_kh,
            last_name_kh=student.last_name_kh,
            first_name_en=student.first_name_en,
            last_name_en=student.last_name_en,
            gender=student.gender.value if hasattr(student.gender, "value") else str(student.gender),
            dob=student.dob, 
            current_grade_level=student.current_grade_level,
            photo_url=student.photo_url,
            

            status=student.status.value if hasattr(student.status, "value") else str(student.status),
            
            created_at=student.created_at,
            updated_at=student.updated_at
        )