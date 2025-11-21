# app/contexts/school/mapper/subject_mapper.py

from app.contexts.school.domain.subject import Subject


class SubjectMapper:
    """
    Handles conversion between Subject domain model and MongoDB dict.
    """

    @staticmethod
    def to_domain(data: dict | Subject) -> Subject:
        if isinstance(data, Subject):
            return data

        return Subject(
            id=data.get("_id"),
            name=data["name"],
            code=data["code"],
            description=data.get("description"),
            allowed_grade_levels=data.get("allowed_grade_levels", []),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def to_persistence(subject: Subject) -> dict:
        return {
            "_id": subject.id,
            "name": subject.name,
            "code": subject.code,
            "description": subject.description,
            "allowed_grade_levels": list(subject.allowed_grade_levels),
            "is_active": subject.is_active,
            "created_at": subject.created_at,
            "updated_at": subject.updated_at,
        }