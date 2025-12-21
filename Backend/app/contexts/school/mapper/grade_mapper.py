from __future__ import annotations

from bson import ObjectId

from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.shared.lifecycle.domain import Lifecycle

class GradeMapper:
    @staticmethod
    def to_domain(data: dict | GradeRecord) -> GradeRecord:
        if isinstance(data, GradeRecord):
            return data

        raw_id = data.get("_id") or data.get("id") or ObjectId()

        lc_raw = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=lc_raw.get("created_at"),
            updated_at=lc_raw.get("updated_at"),
            deleted_at=lc_raw.get("deleted_at"),
            deleted_by=lc_raw.get("deleted_by"),
        )

        raw_type = data.get("type", GradeType.EXAM.value)

        return GradeRecord(
            id=raw_id,
            student_id=data["student_id"],
            subject_id=data["subject_id"],
            class_id=data.get("class_id"),
            teacher_id=data.get("teacher_id"),
            term=data.get("term"),
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
            "term": grade.term,
            "type": grade.type.value if isinstance(grade.type, GradeType) else str(grade.type),
            "score": grade.score,
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
        }