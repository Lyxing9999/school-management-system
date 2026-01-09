from __future__ import annotations

from datetime import datetime, date as date_type
from typing import Any, Optional
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.shared.lifecycle.domain import Lifecycle


class AttendanceMapper:
    @staticmethod
    def _parse_object_id(raw: Any) -> Optional[ObjectId]:
        if raw is None:
            return None
        if isinstance(raw, ObjectId):
            return raw
        try:
            s = str(raw).strip()
            if not s:
                return None
            return ObjectId(s)
        except Exception:
            return None

    @staticmethod
    def _require_object_id(raw: Any, field: str) -> ObjectId:
        oid = AttendanceMapper._parse_object_id(raw)
        if not oid:
            raise ValueError(f"Invalid ObjectId for {field}: {raw!r}")
        return oid

    @staticmethod
    def _parse_datetime(raw: Any) -> Optional[datetime]:
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return raw
        if isinstance(raw, str):
            s = raw.strip()
            if not s:
                return None
            try:
                # Handles "Z"
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            except Exception:
                return None
        return None

    @staticmethod
    def _parse_record_date(raw: Any) -> Optional[date_type]:
        if raw is None:
            return None
        if isinstance(raw, date_type) and not isinstance(raw, datetime):
            return raw
        if isinstance(raw, datetime):
            return raw.date()
        if isinstance(raw, str):
            s = raw.strip()
            if not s:
                return None
            # Accept "YYYY-MM-DD" and ISO datetimes
            try:
                return date_type.fromisoformat(s)
            except ValueError:
                try:
                    return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
                except Exception:
                    return None
        return None

    @staticmethod
    def _require_record_date(raw: Any) -> date_type:
        d = AttendanceMapper._parse_record_date(raw)
        if not d:
            raise ValueError(f"record_date is required and must be ISO date. got={raw!r}")
        return d

    @staticmethod
    def _parse_status(raw: Any) -> AttendanceStatus:
        if isinstance(raw, AttendanceStatus):
            return raw
        if isinstance(raw, str):
            v = raw.strip().lower()
            return AttendanceStatus(v)  # let ValueError bubble if invalid
        # If backend stored enum value directly, you can expand here if needed
        raise ValueError(f"Invalid attendance status: {raw!r}")

    @staticmethod
    def to_domain(data: dict | AttendanceRecord) -> AttendanceRecord:
        if isinstance(data, AttendanceRecord):
            return data

        # Support legacy field name "date"
        raw_date = data.get("record_date") if "record_date" in data else data.get("date")
        record_date = AttendanceMapper._require_record_date(raw_date)

        status = AttendanceMapper._parse_status(
            data.get("status", AttendanceStatus.PRESENT.value)
        )

        lc_raw = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=AttendanceMapper._parse_datetime(lc_raw.get("created_at") or data.get("created_at")),
            updated_at=AttendanceMapper._parse_datetime(lc_raw.get("updated_at") or data.get("updated_at")),
            deleted_at=AttendanceMapper._parse_datetime(lc_raw.get("deleted_at") or data.get("deleted_at")),
            deleted_by=AttendanceMapper._parse_object_id(lc_raw.get("deleted_by") or data.get("deleted_by")),
        )

        return AttendanceRecord(
            id=AttendanceMapper._parse_object_id(data.get("_id")) or AttendanceMapper._parse_object_id(data.get("id")),
            student_id=AttendanceMapper._require_object_id(data.get("student_id"), "student_id"),
            class_id=AttendanceMapper._require_object_id(data.get("class_id"), "class_id"),
            subject_id=AttendanceMapper._require_object_id(data.get("subject_id"), "subject_id"),
            schedule_slot_id=AttendanceMapper._require_object_id(data.get("schedule_slot_id"), "schedule_slot_id"),
            status=status,
            record_date=record_date,
            marked_by_teacher_id=AttendanceMapper._parse_object_id(data.get("marked_by_teacher_id")),
            lifecycle=lifecycle,
        )

    @staticmethod
    def to_persistence(record: AttendanceRecord) -> dict:
        lc = record.lifecycle

        if record.record_date is None:
            # If you decide record_date is required, fail loudly here too.
            raise ValueError("AttendanceRecord.record_date is required")

        return {
            "_id": record.id,
            "student_id": record.student_id,
            "class_id": record.class_id,
            "subject_id": record.subject_id,
            "schedule_slot_id": record.schedule_slot_id,
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
