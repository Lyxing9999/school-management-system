# app/contexts/school/mapper/attendance_mapper.py

from __future__ import annotations
from datetime import date as date_type, datetime, time

from app.contexts.school.domain.attendance import (
    AttendanceRecord,
    AttendanceStatus,
)


class AttendanceMapper:
    """
    Handles conversion between AttendanceRecord domain model and MongoDB dict.
    """

    @staticmethod
    def to_domain(data: dict | AttendanceRecord) -> AttendanceRecord:
        if isinstance(data, AttendanceRecord):
            return data

        raw_date = data.get("record_date")
        if isinstance(raw_date, datetime):
            record_date = raw_date.date()
        elif isinstance(raw_date, date_type):
            record_date = raw_date
        elif raw_date is None:
            record_date = None
        else:
            record_date = datetime.fromisoformat(raw_date).date()

        raw_status = data.get("status", AttendanceStatus.PRESENT)
        if isinstance(raw_status, AttendanceStatus):
            status = raw_status
        else:
            try:
                status = AttendanceStatus(raw_status)
            except ValueError:
                status = AttendanceStatus.PRESENT

        return AttendanceRecord(
            id=data.get("_id"),
            student_id=data["student_id"],
            class_id=data["class_id"],
            status=status,
            record_date=record_date,              # keep domain param name as your model expects
            marked_by_teacher_id=data.get("marked_by_teacher_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def to_persistence(record: AttendanceRecord) -> dict:
        """
        Ensure record_date is a datetime for MongoDB (not a date).
        Try both `record.record_date` and `record.date` to match your domain model.
        """
        # Try the main name
        raw_date = getattr(record, "record_date", None)
        # Fallback to `date` if your domain class uses that
        if raw_date is None:
            raw_date = getattr(record, "date", None)

        if isinstance(raw_date, datetime):
            mongo_record_date = raw_date
        elif isinstance(raw_date, date_type):
            mongo_record_date = datetime.combine(raw_date, time.min)
        elif raw_date is None:
            mongo_record_date = None
        else:
            mongo_record_date = datetime.fromisoformat(raw_date)

        return {
            "_id": record.id,
            "student_id": record.student_id,
            "class_id": record.class_id,
            "status": (
                record.status.value
                if isinstance(record.status, AttendanceStatus)
                else record.status
            ),
            "record_date": mongo_record_date,
            "marked_by_teacher_id": record.marked_by_teacher_id,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }