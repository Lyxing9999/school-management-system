from __future__ import annotations

from typing import Optional
from datetime import date as date_type
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.errors.attendance_exceptions import AttendanceNotFoundException

from ._base import OidMixin


class AttendanceService(OidMixin):
    def __init__(self, *, attendance_repo, attendance_factory):
        self.attendance_repo = attendance_repo
        self.attendance_factory = attendance_factory

    def mark_attendance(
        self,
        student_id: str | ObjectId,
        class_id: str | ObjectId,
        status: AttendanceStatus | str,
        teacher_id: str | ObjectId,
        record_date: date_type | None = None,
    ) -> AttendanceRecord:
        record = self.attendance_factory.create_record(
            student_id=student_id,
            class_id=class_id,
            status=status,
            teacher_id=teacher_id,
            record_date=record_date,
        )
        return self.attendance_repo.insert(record)

    def change_attendance_status(
        self,
        attendance_id: str | ObjectId,
        new_status: AttendanceStatus | str,
    ) -> Optional[AttendanceRecord]:
        oid = self._oid(attendance_id)
        existing = self.attendance_repo.find_by_id(oid)
        if existing is None:
            raise AttendanceNotFoundException(attendance_id)

        existing.change_status(new_status)  # domain handles validation
        return self.attendance_repo.update(existing)

    def get_attendance_by_id(self, attendance_id: str | ObjectId) -> Optional[AttendanceRecord]:
        return self.attendance_repo.find_by_id(self._oid(attendance_id))