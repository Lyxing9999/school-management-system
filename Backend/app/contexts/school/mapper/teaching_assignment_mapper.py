from __future__ import annotations
from typing import Any, Optional
from datetime import datetime

from bson import ObjectId

from app.contexts.school.domain.teaching_assignment import TeachingAssignmentRecord
from app.contexts.shared.lifecycle.domain import Lifecycle

class TeachingAssignmentMapper:
    @staticmethod
    def _parse_oid(raw: Any) -> Optional[ObjectId]:
        if raw is None:
            return None
        if isinstance(raw, ObjectId):
            return raw
        try:
            return ObjectId(str(raw))
        except Exception:
            return None

    @staticmethod
    def _parse_dt(raw: Any) -> Optional[datetime]:
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
    def to_domain(doc: dict) -> TeachingAssignmentRecord:
        lc = doc.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=TeachingAssignmentMapper._parse_dt(lc.get("created_at")),
            updated_at=TeachingAssignmentMapper._parse_dt(lc.get("updated_at")),
            deleted_at=TeachingAssignmentMapper._parse_dt(lc.get("deleted_at")),
            deleted_by=TeachingAssignmentMapper._parse_oid(lc.get("deleted_by")),
        )

        return TeachingAssignmentRecord(
            id=doc.get("_id"),
            class_id=doc["class_id"],
            subject_id=doc["subject_id"],
            teacher_id=doc["teacher_id"],
            assigned_by=doc.get("assigned_by"),
            lifecycle=lifecycle,
        )

    @staticmethod
    def to_persistence(entity: TeachingAssignmentRecord) -> dict:
        lc = entity.lifecycle
        return {
            "_id": entity.id,
            "class_id": entity.class_id,
            "subject_id": entity.subject_id,
            "teacher_id": entity.teacher_id,
            "assigned_by": entity.assigned_by,
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
        }