from __future__ import annotations

from app.contexts.school.domain.subject import Subject
from app.contexts.shared.lifecycle.domain import Lifecycle


class SubjectMapper:
    @staticmethod
    def to_domain(data: dict | Subject) -> Subject:
        if isinstance(data, Subject):
            return data

        lc_raw = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=lc_raw.get("created_at"),
            updated_at=lc_raw.get("updated_at"),
            deleted_at=lc_raw.get("deleted_at"),
            deleted_by=lc_raw.get("deleted_by"),
        )

        return Subject(
            id=data.get("_id"),
            name=data["name"],
            code=data["code"],
            description=data.get("description"),
            allowed_grade_levels=data.get("allowed_grade_levels", []),
            is_active=data.get("is_active", True),
            lifecycle=lifecycle,
        )

    @staticmethod
    def to_persistence(subject: Subject) -> dict:
        lc = subject.lifecycle
        return {
            "_id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "allowed_grade_levels": list(subject.allowed_grade_levels),
            "is_active": subject.is_active,
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
        }