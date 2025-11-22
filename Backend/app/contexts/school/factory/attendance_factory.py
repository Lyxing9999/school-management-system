from __future__ import annotations
from datetime import date as date_type
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.errors.attendance_exceptions import (
    NotClassTeacherException,
    StudentNotEnrolledInClassException,
    AttendanceAlreadyMarkedException,
)
from app.contexts.school.errors.class_exceptions import ClassNotFoundException 
from app.contexts.shared.model_converter import mongo_converter


class AttendanceFactory:
    """
    Factory for creating AttendanceRecord domain objects with business checks.

    Responsibilities:
    - Ensure teacher is assigned to the class
    - Ensure student is enrolled in the class
    - Prevent duplicate attendance for same class + student + date
    """

    def __init__(self, class_read_model, enrollment_read_model, attendance_read_model):
        """
        :param class_read_model: provides:
            - get_by_id(class_id) -> dict | None
        :param enrollment_read_model: provides:
            - is_student_enrolled(student_id, class_id) -> bool
        :param attendance_read_model: provides:
            - get_by_student_class_date(student_id, class_id, date) -> dict | None
        """
        self.class_read_model = class_read_model
        self.enrollment_read_model = enrollment_read_model
        self.attendance_read_model = attendance_read_model

    # ------------ internal helpers ------------

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        """
        Convert incoming id to ObjectId using shared converter.
        """
        return mongo_converter.convert_to_object_id(id_)
    
    def create_record(
        self,
        student_id: str | ObjectId,
        class_id: str | ObjectId,
        status: AttendanceStatus | str,
        teacher_id: str | ObjectId,
        record_date: date_type | None = None,
    ) -> AttendanceRecord:
        # Normalize IDs
        student_obj_id = self._normalize_id(student_id)
        class_obj_id = self._normalize_id(class_id)
        teacher_obj_id = self._normalize_id(teacher_id)

        class_doc = self.class_read_model.get_by_id(class_obj_id)
        if not class_doc:
            raise ClassNotFoundException(class_obj_id)

        if class_doc.get("teacher_id") != teacher_obj_id:
            raise NotClassTeacherException(teacher_obj_id, class_obj_id)

        if not self.enrollment_read_model.is_student_enrolled(student_obj_id, class_obj_id):
            raise StudentNotEnrolledInClassException(student_obj_id, class_obj_id)

        date_to_use = record_date or None
        existing = self.attendance_read_model.get_by_student_class_date(
            student_id=student_obj_id,
            class_id=class_obj_id,
            record_date=date_to_use,
        )
        if existing:
            raise AttendanceAlreadyMarkedException(student_obj_id, class_obj_id, date_to_use)

        return AttendanceRecord(
            student_id=student_obj_id,
            class_id=class_obj_id,
            status=status,
            record_date=date_to_use,
            marked_by_teacher_id=teacher_obj_id,
        )