# app/contexts/school/mapper/grade_mapper.py

from app.contexts.school.domain.grade import GradeRecord, GradeType


class GradeMapper:
    """
    Handles conversion between GradeRecord domain model and MongoDB dict.
    """

    @staticmethod
    def to_domain(data: dict | GradeRecord) -> GradeRecord:
        if isinstance(data, GradeRecord):
            return data

        return GradeRecord(
            id=data.get("_id"),
            student_id=data["student_id"],
            subject_id=data["subject_id"],
            score=data["score"],
            type=data.get("type", GradeType.EXAM),
            class_id=data.get("class_id"),
            teacher_id=data.get("teacher_id"),
            term=data.get("term"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def to_persistence(grade: GradeRecord) -> dict:
        return {
            "_id": grade.id,
            "student_id": grade.student_id,
            "subject_id": grade.subject_id,
            "class_id": grade.class_id,
            "teacher_id": grade.teacher_id,
            "term": grade.term,
            "type": grade.type.value,
            "score": grade.score,
            "created_at": grade.created_at,
            "updated_at": grade.updated_at,
        }