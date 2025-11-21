import pytest
from datetime import datetime
from bson import ObjectId

from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.errors.grade_exceptions import (
    InvalidGradeTypeException,
    InvalidGradeScoreException,
    GradeTypeChangeForbiddenException,
)


def test_grade_record_init_valid_exam():
    student_id = ObjectId()
    subject_id = ObjectId()

    record = GradeRecord(
        student_id=student_id,
        subject_id=subject_id,
        score=85.5,
        type=GradeType.EXAM,
        term="2025-S1",
    )

    assert record.id is not None
    assert record.student_id == student_id
    assert record.subject_id == subject_id
    assert record.class_id is None
    assert record.teacher_id is None
    assert record.term == "2025-S1"
    assert record.type == GradeType.EXAM
    assert record.score == pytest.approx(85.5)
    assert isinstance(record.created_at, datetime)
    assert isinstance(record.updated_at, datetime)


def test_grade_record_init_with_string_type():
    student_id = ObjectId()
    subject_id = ObjectId()

    record = GradeRecord(
        student_id=student_id,
        subject_id=subject_id,
        score=70,
        type="assignment",  # string input
    )

    assert record.type == GradeType.ASSIGNMENT


def test_grade_record_invalid_type_raises():
    student_id = ObjectId()
    subject_id = ObjectId()

    with pytest.raises(InvalidGradeTypeException):
        GradeRecord(
            student_id=student_id,
            subject_id=subject_id,
            score=50,
            type="quiz",  # not exam/assignment
        )


def test_grade_record_invalid_score_below_zero_raises():
    student_id = ObjectId()
    subject_id = ObjectId()

    with pytest.raises(InvalidGradeScoreException):
        GradeRecord(
            student_id=student_id,
            subject_id=subject_id,
            score=-1,
            type=GradeType.EXAM,
        )


def test_grade_record_invalid_score_above_100_raises():
    student_id = ObjectId()
    subject_id = ObjectId()

    with pytest.raises(InvalidGradeScoreException):
        GradeRecord(
            student_id=student_id,
            subject_id=subject_id,
            score=101,
            type=GradeType.EXAM,
        )


def test_set_score_updates_value_and_timestamp():
    student_id = ObjectId()
    subject_id = ObjectId()

    record = GradeRecord(
        student_id=student_id,
        subject_id=subject_id,
        score=50,
        type=GradeType.EXAM,
    )
    old_updated_at = record.updated_at

    record.set_score(90)

    assert record.score == pytest.approx(90.0)
    assert record.updated_at > old_updated_at


def test_set_score_invalid_after_init_raises():
    student_id = ObjectId()
    subject_id = ObjectId()

    record = GradeRecord(
        student_id=student_id,
        subject_id=subject_id,
        score=50,
        type=GradeType.EXAM,
    )

    with pytest.raises(InvalidGradeScoreException):
        record.set_score(200)


def test_change_type_allowed_when_score_zero():
    student_id = ObjectId()
    subject_id = ObjectId()

    record = GradeRecord(
        student_id=student_id,
        subject_id=subject_id,
        score=0,
        type=GradeType.EXAM,
    )
    old_updated_at = record.updated_at

    record.change_type(GradeType.ASSIGNMENT)

    assert record.type == GradeType.ASSIGNMENT
    assert record.updated_at > old_updated_at


def test_change_type_forbidden_when_score_positive():
    student_id = ObjectId()
    subject_id = ObjectId()

    record = GradeRecord(
        student_id=student_id,
        subject_id=subject_id,
        score=50,
        type=GradeType.EXAM,
    )

    with pytest.raises(GradeTypeChangeForbiddenException):
        record.change_type(GradeType.ASSIGNMENT)


def test_ids_are_normalized_from_strings():
    student_id = ObjectId()
    subject_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()

    record = GradeRecord(
        student_id=str(student_id),
        subject_id=str(subject_id),
        class_id=str(class_id),
        teacher_id=str(teacher_id),
        score=75,
        type=GradeType.EXAM,
    )

    assert isinstance(record.student_id, ObjectId)
    assert isinstance(record.subject_id, ObjectId)
    assert isinstance(record.class_id, ObjectId)
    assert isinstance(record.teacher_id, ObjectId)

    assert record.student_id == student_id
    assert record.subject_id == subject_id
    assert record.class_id == class_id
    assert record.teacher_id == teacher_id