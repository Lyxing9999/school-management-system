
from app.contexts.school.domain.class_section import ClassSection


class ClassSectionMapper:
    """
    Handles conversion between ClassSection domain model and MongoDB dict.
    """

    @staticmethod
    def to_domain(data: dict | ClassSection) -> ClassSection:
        if isinstance(data, ClassSection):
            return data

        return ClassSection(
            id=data.get("_id"),
            name=data["name"],
            teacher_id=data.get("teacher_id"),
            enrolled_count=data.get("enrolled_count", 0),
            subject_ids=data.get("subject_ids", []),
            max_students=data.get("max_students"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deleted=data.get("deleted", False),
        )

    @staticmethod
    def to_persistence(cls: ClassSection) -> dict:
        return {
            "_id": cls.id,
            "name": cls.name,
            "teacher_id": cls.teacher_id,
            "enrolled_count": cls.enrolled_count,
            "subject_ids": list(cls.subject_ids),
            "max_students": cls.max_students,
            "created_at": cls.created_at,
            "updated_at": cls.updated_at,
            "deleted": cls.deleted,
        }