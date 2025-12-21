from __future__ import annotations

from datetime import date as date_type
from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.shared.lifecycle.domain import Lifecycle


class AttendanceMapper:
    """
    Persistence decisions:
    - store attendance date as ISO string 'YYYY-MM-DD' to avoid timezone bugs
    - store lifecycle nested
    """

    @staticmethod
    def to_domain(data: dict | AttendanceRecord) -> AttendanceRecord:
        if isinstance(data, AttendanceRecord):
            return data
        raw_date = data.get("record_date")
        record_date = date_type.fromisoformat(raw_date) if isinstance(raw_date, str) else None

        # Status
        raw_status = data.get("status", AttendanceStatus.PRESENT.value)
        try:
            status = AttendanceStatus(raw_status) if not isinstance(raw_status, AttendanceStatus) else raw_status
        except ValueError:
            status = AttendanceStatus.PRESENT

        # Lifecycle
        lc_raw = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=lc_raw.get("created_at"),
            updated_at=lc_raw.get("updated_at"),
            deleted_at=lc_raw.get("deleted_at"),
            deleted_by=lc_raw.get("deleted_by"),
        )

        return AttendanceRecord(
            id=data.get("_id"),
            student_id=data["student_id"],
            class_id=data["class_id"],
            status=status,
            record_date=record_date,
            marked_by_teacher_id=data.get("marked_by_teacher_id"),
            lifecycle=lifecycle,
        )

    @staticmethod
    def to_persistence(record: AttendanceRecord) -> dict:
        lc = record.lifecycle
        return {
            "_id": record.id,
            "student_id": record.student_id,
            "class_id": record.class_id,
            "status": record.status.value,
            "record_date": record.date.isoformat(),
            "marked_by_teacher_id": record.marked_by_teacher_id,
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
        }