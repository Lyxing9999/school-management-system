
from datetime import datetime
from bson import ObjectId

from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.mapper.grade_mapper import GradeMapper


def test_to_domain_from_full_dict():
    rec_id = ObjectId()
    student_id = ObjectId()
    subject_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()
    created_at = datetime(2025, 1, 1, 8, 0, 0)
    updated_at = datetime(2025, 1, 1, 9, 0, 0)

    data = {
        "_id": rec_id,
        "student_id": student_id,
        "subject_id": subject_id,
        "class_id": class_id,
        "teacher_id": teacher_id,
        "term": "2025-S1",
        "type": "assignment",
        "score": 95.0,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    grade = GradeMapper.to_domain(data)

    assert isinstance(grade, GradeRecord)
    assert grade.id == rec_id
    assert grade.student_id == student_id
    assert grade.subject_id == subject_id
    assert grade.class_id == class_id
    assert grade.teacher_id == teacher_id
    assert grade.term == "2025-S1"
    assert grade.type == GradeType.ASSIGNMENT
    assert grade.score == 95.0
    assert grade.created_at == created_at
    assert grade.updated_at == updated_at


def test_to_domain_defaults_type_to_exam_when_missing():
    data = {
        "_id": ObjectId(),
        "student_id": ObjectId(),
        "subject_id": ObjectId(),
        "score": 77.0,
        # no "type" field
    }

    grade = GradeMapper.to_domain(data)

    assert grade.type == GradeType.EXAM
    assert grade.score == 77.0

def test_to_domain_when_already_domain_returns_same_instance():
    student_id = ObjectId()
    subject_id = ObjectId()

    original = GradeRecord(
        student_id=student_id,
        subject_id=subject_id,
        score=80.0,
        type=GradeType.EXAM,
    )

    result = GradeMapper.to_domain(original)

    assert result is original


def test_to_persistence_builds_correct_dict():
    student_id = ObjectId()
    subject_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()

    grade = GradeRecord(
        student_id=student_id,
        subject_id=subject_id,
        score=60.5,
        type=GradeType.ASSIGNMENT,
        class_id=class_id,
        teacher_id=teacher_id,
        term="2025-S2",
    )

    data = GradeMapper.to_persistence(grade)

    assert data["_id"] == grade.id
    assert data["student_id"] == student_id
    assert data["subject_id"] == subject_id
    assert data["class_id"] == class_id
    assert data["teacher_id"] == teacher_id
    assert data["term"] == "2025-S2"
    assert data["type"] == "assignment"
    assert data["score"] == 60.5
    assert data["created_at"] == grade.created_at
    assert data["updated_at"] == grade.updated_at