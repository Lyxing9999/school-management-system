# app/contexts/school/mapper/attendance_mapper.py

from datetime import datetime, date as date_type
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

        # Normalize date: could be stored as datetime or date
        raw_date = data.get("date")
        record_date: date_type | None = None
        if isinstance(raw_date, datetime):
            record_date = raw_date.date()
        elif isinstance(raw_date, date_type):
            record_date = raw_date
        elif raw_date is None:
            record_date = None
        else:
            # If you store as ISO string, parse here
            record_date = datetime.fromisoformat(raw_date).date()

        return AttendanceRecord(
            id=data.get("_id"),
            student_id=data["student_id"],
            class_id=data["class_id"],
            status=data.get("status", AttendanceStatus.PRESENT),
            record_date=record_date,
            marked_by_teacher_id=data.get("marked_by_teacher_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def to_persistence(record: AttendanceRecord) -> dict:
        return {
            "_id": record.id,
            "student_id": record.student_id,
            "class_id": record.class_id,
            "status": record.status.value,
            "date": record.date,  # can be stored as date/datetime by PyMongo
            "marked_by_teacher_id": record.marked_by_teacher_id,
            "created_at": record.created_at,
            "updated_at": record.updated_at,
        }