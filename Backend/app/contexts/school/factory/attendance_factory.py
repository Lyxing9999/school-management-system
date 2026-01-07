
from datetime import date as date_type
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus, today_kh
from app.contexts.school.domain.class_section import ClassSectionStatus
from app.contexts.school.errors.attendance_exceptions import (
    NotClassTeacherException,
    AttendanceAlreadyMarkedException,
)
from app.contexts.school.errors.class_exceptions import ClassNotFoundException, ClassSectionNotActiveException
from app.contexts.shared.model_converter import mongo_converter

class AttendanceFactory:
    def __init__(self, class_read_model, attendance_read_model):
        self.class_read_model = class_read_model
        self.attendance_read_model = attendance_read_model

    def _oid(self, value: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(value)

    def create_record(
        self,
        *,
        student_id: str | ObjectId,
        class_id: str | ObjectId,
        status: AttendanceStatus | str,
        teacher_id: str | ObjectId,
        record_date: date_type | None = None,
    ) -> AttendanceRecord:
        student_oid = self._oid(student_id)
        class_oid = self._oid(class_id)
        teacher_oid = self._oid(teacher_id)

        class_doc = self.class_read_model.get_by_id(class_oid)
        if not class_doc:
            raise ClassNotFoundException(class_oid)

        if class_doc.get("status") != ClassSectionStatus.ACTIVE.value:
            raise ClassSectionNotActiveException()

        if class_doc.get("teacher_id") != teacher_oid:
            raise NotClassTeacherException(teacher_oid, class_oid)

        effective_date = record_date or today_kh()

        existing = self.attendance_read_model.get_by_student_class_date(
            student_id=student_oid,
            class_id=class_oid,
            record_date=effective_date,
            show_deleted="active",
        )
        if existing:
            raise AttendanceAlreadyMarkedException(
                student_oid,
                class_oid,
                effective_date.isoformat(),
            )

        return AttendanceRecord(
            student_id=student_oid,
            class_id=class_oid,
            status=status,
            record_date=effective_date,
            marked_by_teacher_id=teacher_oid,
        )