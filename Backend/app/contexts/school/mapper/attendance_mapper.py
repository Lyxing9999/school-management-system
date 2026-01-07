
from datetime import datetime, date as date_type
from typing import Any, Optional

from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.shared.lifecycle.domain import Lifecycle


class AttendanceMapper:
    """
    Persistence decisions:
    - store record_date as ISO string 'YYYY-MM-DD' (KH school date)
    - store lifecycle nested
    """

    # ---------- parsing helpers ----------

    @staticmethod
    def _parse_object_id(raw: Any) -> Optional[ObjectId]:
        if raw is None:
            return None
        if isinstance(raw, ObjectId):
            return raw
        try:
            return ObjectId(str(raw))
        except Exception:
            return None

    @staticmethod
    def _parse_datetime(raw: Any) -> Optional[datetime]:
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return raw
        if isinstance(raw, str):
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except Exception:
                return None
        return None

    @staticmethod
    def _parse_record_date(raw: Any) -> Optional[date_type]:
        """
        Backward compatible:
        - if stored as 'YYYY-MM-DD' string -> parse
        - if stored as datetime -> take .date()
        - if stored as date -> use directly
        """
        if raw is None:
            return None
        if isinstance(raw, date_type) and not isinstance(raw, datetime):
            return raw
        if isinstance(raw, datetime):
            return raw.date()
        if isinstance(raw, str):
            try:
                return date_type.fromisoformat(raw)
            except ValueError:
                # also accept ISO datetime strings
                try:
                    return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
                except Exception:
                    return None
        return None

    @staticmethod
    def _parse_status(raw: Any) -> AttendanceStatus:
        if isinstance(raw, AttendanceStatus):
            return raw
        if isinstance(raw, str):
            # normalize common accidental formats
            v = raw.strip().lower()
            try:
                return AttendanceStatus(v)
            except ValueError:
                return AttendanceStatus.PRESENT
        return AttendanceStatus.PRESENT

    # ---------- public API ----------

    @staticmethod
    def to_domain(data: dict | AttendanceRecord) -> AttendanceRecord:
        if isinstance(data, AttendanceRecord):
            return data

        record_date = AttendanceMapper._parse_record_date(
            data.get("record_date") if "record_date" in data else data.get("date")
        )

        status = AttendanceMapper._parse_status(data.get("status", AttendanceStatus.PRESENT.value))

        lc_raw = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=AttendanceMapper._parse_datetime(lc_raw.get("created_at") or data.get("created_at")),
            updated_at=AttendanceMapper._parse_datetime(lc_raw.get("updated_at") or data.get("updated_at")),
            deleted_at=AttendanceMapper._parse_datetime(lc_raw.get("deleted_at") or data.get("deleted_at")),
            deleted_by=AttendanceMapper._parse_object_id(lc_raw.get("deleted_by") or data.get("deleted_by")),
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
            "record_date": record.record_date.isoformat(),
            "marked_by_teacher_id": record.marked_by_teacher_id,
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
        }