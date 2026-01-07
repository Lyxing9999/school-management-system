from __future__ import annotations

from app.contexts.school.domain.class_section import ClassSection, ClassSectionStatus
from app.contexts.shared.lifecycle.domain import Lifecycle


class ClassSectionMapper:
    @staticmethod
    def to_domain(data: dict | ClassSection) -> ClassSection:
        if isinstance(data, ClassSection):
            return data

        lc_raw = data.get("lifecycle") or {}
        lifecycle = Lifecycle(
            created_at=lc_raw.get("created_at"),
            updated_at=lc_raw.get("updated_at"),
            deleted_at=lc_raw.get("deleted_at"),
            deleted_by=lc_raw.get("deleted_by"),
        )

        status_raw = data.get("status") or ClassSectionStatus.ACTIVE.value

        return ClassSection(
            name=data["name"],
            id=data.get("_id"),
            homeroom_teacher_id=data.get("homeroom_teacher_id"),
            enrolled_count=data.get("enrolled_count", 0),
            subject_ids=data.get("subject_ids", []),
            max_students=data.get("max_students"),
            status=status_raw, 
            lifecycle=lifecycle,
        )

    @staticmethod
    def to_persistence(cls: ClassSection) -> dict:
        lc = cls.lifecycle
        return {
            "_id": cls.id,
            "name": cls.name,
            "homeroom_teacher_id": cls.homeroom_teacher_id,
            "enrolled_count": cls.enrolled_count,
            "subject_ids": list(cls.subject_ids),
            "max_students": cls.max_students,
            "status": cls.status.value,
            "lifecycle": {
                "created_at": lc.created_at,
                "updated_at": lc.updated_at,
                "deleted_at": lc.deleted_at,
                "deleted_by": lc.deleted_by,
            },
        }