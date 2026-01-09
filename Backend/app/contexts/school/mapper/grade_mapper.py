from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from bson import ObjectId

from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.errors.grade_exceptions import InvalidTermException
from app.contexts.shared.lifecycle.domain import Lifecycle


class GradeMapper:
    # ---------- parsing helpers ----------

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
                # supports "...Z" and full ISO
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            except Exception:
                return None
        if isinstance(raw, dict) and "$date" in raw:
            return GradeMapper._parse_datetime(raw["$date"])
        return None

    @staticmethod
    def _coerce_grade_type(raw: Any) -> GradeType | str:
        """
        Let GradeRecord validate/raise domain exception.
        We just provide a best-effort normalization.
        """
        if isinstance(raw, GradeType):
            return raw
        if isinstance(raw, str):
            return raw.strip().lower()
        return str(raw)

    @staticmethod
    def _require_term(raw_term: Any) -> str:
        """
        Enforce term required at persistence boundary.
        GradeRecord will validate format (YYYY-S1 / YYYY-S2) anyway.
        """
        if raw_term is None:
            raise InvalidTermException(received_value=None, expected="YYYY-S1 or YYYY-S2")

        if isinstance(raw_term, str):
            t = raw_term.strip()
            if not t:
                raise InvalidTermException(received_value=raw_term, expected="YYYY-S1 or YYYY-S2")
            return t

        # fallback: convert to string
        t = str(raw_term).strip()
        if not t:
            raise InvalidTermException(received_value=raw_term, expected="YYYY-S1 or YYYY-S2")
        return t

    # ---------- main mapping ----------

    @staticmethod
    def to_domain(data: dict | GradeRecord) -> GradeRecord:
        if isinstance(data, GradeRecord):
            return data

        raw_id = data.get("_id") or data.get("id") or ObjectId()

        # lifecycle: accept dict OR flat fields
        lc_raw = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=GradeMapper._parse_datetime(lc_raw.get("created_at") or data.get("created_at")),
            updated_at=GradeMapper._parse_datetime(lc_raw.get("updated_at") or data.get("updated_at")),
            deleted_at=GradeMapper._parse_datetime(lc_raw.get("deleted_at") or data.get("deleted_at")),
            deleted_by=GradeMapper._parse_object_id(lc_raw.get("deleted_by") or data.get("deleted_by")),
        )

        raw_type = GradeMapper._coerce_grade_type(data.get("type", GradeType.EXAM.value))

        # TERM REQUIRED: enforce here
        term = GradeMapper._require_term(data.get("term"))

        return GradeRecord(
            id=raw_id,
            student_id=data["student_id"],
            subject_id=data["subject_id"],
            class_id=data.get("class_id"),
            teacher_id=data.get("teacher_id"),
            term=term,
            type=raw_type,
            score=data["score"],
            lifecycle=lifecycle,
        )

    @staticmethod
    def to_persistence(grade: GradeRecord) -> dict:
        lc = grade.lifecycle
        return {
            "_id": grade.id,
            "student_id": grade.student_id,
            "subject_id": grade.subject_id,
            "class_id": grade.class_id,
            "teacher_id": grade.teacher_id,
            "term": grade.term,  # required
            "type": grade.type.value if isinstance(grade.type, GradeType) else str(grade.type),
            "score": float(grade.score),
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
        }