from __future__ import annotations

from datetime import date as date_type
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.errors.attendance_exceptions import (
    NotClassTeacherException,
    AttendanceAlreadyMarkedException,
)
from app.contexts.school.errors.class_exceptions import ClassNotFoundException
from app.contexts.shared.model_converter import mongo_converter


class AttendanceFactory:
    """
    Factory for creating AttendanceRecord with business checks:
    - teacher must be assigned to class
    - no duplicate (student, class, date)
    """

    def __init__(self, class_read_model, attendance_read_model):
        self.class_read_model = class_read_model
        self.attendance_read_model = attendance_read_model

    def _normalize_id(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    def create_record(
        self,
        *,
        student_id: str | ObjectId,
        class_id: str | ObjectId,
        status: AttendanceStatus | str,
        teacher_id: str | ObjectId,
        record_date: date_type | None = None,
    ) -> AttendanceRecord:
        student_oid = self._normalize_id(student_id)
        class_oid = self._normalize_id(class_id)
        teacher_oid = self._normalize_id(teacher_id)

        class_doc = self.class_read_model.get_by_id(class_oid)
        if not class_doc:
            raise ClassNotFoundException(class_oid)

        if class_doc.get("teacher_id") != teacher_oid:
            raise NotClassTeacherException(teacher_oid, class_oid)

        # record_date can be None -> domain will default to KH today
        existing = self.attendance_read_model.get_by_student_class_date(
            student_id=student_oid,
            class_id=class_oid,
            record_date=record_date,  # pass through; read model should handle None OR caller always supplies
        )
        if existing:
            # For message consistency, use the actual date domain will use
            # If record_date is None, domain will use today_kh(); you can pass None or compute in service.
            raise AttendanceAlreadyMarkedException(student_oid, class_oid, str(record_date))

        return AttendanceRecord(
            student_id=student_oid,
            class_id=class_oid,
            status=status,
            record_date=record_date,            
            marked_by_teacher_id=teacher_oid,
        )