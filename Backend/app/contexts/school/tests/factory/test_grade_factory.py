import pytest
from bson import ObjectId

from app.contexts.school.domain.grade import GradeRecord, GradeType
from app.contexts.school.factory.grade_factory import GradeFactory
from app.contexts.school.errors.grade_exceptions import (
    NotSubjectTeacherException,
    StudentNotEnrolledForSubjectException,
)

# ---- Fake read models (unique to this file) -----------------------


class GFSubjectReadModel:
    def __init__(self, docs_by_id=None):
        self.docs_by_id = docs_by_id or {}
        self.calls = []

    def get_by_id(self, subject_id: ObjectId):
        self.calls.append(subject_id)
        return self.docs_by_id.get(subject_id)


class GFClassReadModel:
    def __init__(self, docs_by_id=None):
        self.docs_by_id = docs_by_id or {}
        self.calls = []

    def get_by_id(self, class_id: ObjectId):
        self.calls.append(class_id)
        return self.docs_by_id.get(class_id)


class GFEnrollmentReadModel:
    def __init__(self, enrolled_pairs=None):
        # set[(student_id, class_id)]
        self.enrolled_pairs = enrolled_pairs or set()
        self.calls = []

    def is_student_enrolled(self, student_id: ObjectId, class_id: ObjectId) -> bool:
        self.calls.append((student_id, class_id))
        return (student_id, class_id) in self.enrolled_pairs


class GFTeacherAssignmentReadModel:
    def __init__(self, allowed_triples=None):
        # set[(teacher_id, class_id, subject_id)]
        self.allowed_triples = allowed_triples or set()
        self.calls = []

    def can_teacher_grade(
        self,
        teacher_id: ObjectId,
        class_id: ObjectId,
        subject_id: ObjectId,
    ) -> bool:
        self.calls.append((teacher_id, class_id, subject_id))
        return (teacher_id, class_id, subject_id) in self.allowed_triples


def _build_grade_factory(
    *,
    subject_exists=True,
    class_exists=True,
    teacher_can_grade=True,
    student_enrolled=True,
):
    subject_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()
    student_id = ObjectId()

    subject_docs = {subject_id: {"_id": subject_id}} if subject_exists else {}
    class_docs = {class_id: {"_id": class_id}} if class_exists else {}

    subject_read = GFSubjectReadModel(subject_docs)
    class_read = GFClassReadModel(class_docs)

    enrolled_pairs = {(student_id, class_id)} if student_enrolled else set()
    enrollment_read = GFEnrollmentReadModel(enrolled_pairs=enrolled_pairs)

    allowed_triples = (
        {(teacher_id, class_id, subject_id)} if teacher_can_grade else set()
    )
    teacher_assignment_read = GFTeacherAssignmentReadModel(allowed_triples=allowed_triples)

    factory = GradeFactory(
        class_read_model=class_read,
        subject_read_model=subject_read,
        enrollment_read_model=enrollment_read,
        teacher_assignment_read_model=teacher_assignment_read,
    )

    return (
        factory,
        student_id,
        subject_id,
        teacher_id,
        class_id,
        subject_read,
        class_read,
        enrollment_read,
        teacher_assignment_read,
    ) 

def test_create_grade_success_with_class_and_subject():
    (
        factory,
        student_id,
        subject_id,
        teacher_id,
        class_id,
        subject_read,
        class_read,
        enrollment_read,
        teacher_assignment_read,
    ) = _build_grade_factory(
        subject_exists=True,
        class_exists=True,
        teacher_can_grade=True,
        student_enrolled=True,
    )

    grade = factory.create_grade(
        student_id=student_id,
        subject_id=subject_id,
        score=85.0,
        type=GradeType.EXAM,
        teacher_id=teacher_id,
        class_id=class_id,
        term="2025-S1",
    )

    assert isinstance(grade, GradeRecord)
    assert grade.student_id == student_id
    assert grade.subject_id == subject_id
    assert grade.class_id == class_id
    assert grade.teacher_id == teacher_id
    assert grade.term == "2025-S1"
    assert grade.score == 85.0
    assert grade.type == GradeType.EXAM

    assert subject_read.calls == [subject_id]
    assert class_read.calls == [class_id]
    assert enrollment_read.calls == [(student_id, class_id)]
    assert teacher_assignment_read.calls == [(teacher_id, class_id, subject_id)]

def test_create_grade_success_without_class_id_skips_teacher_and_enrollment_checks():
    subject_id = ObjectId()
    teacher_id = ObjectId()
    student_id = ObjectId()

    subject_read = GFSubjectReadModel({subject_id: {"_id": subject_id}})
    class_read = GFClassReadModel()
    enrollment_read = GFEnrollmentReadModel()
    teacher_assignment_read = GFTeacherAssignmentReadModel()

    factory = GradeFactory(
        class_read_model=class_read,
        subject_read_model=subject_read,
        enrollment_read_model=enrollment_read,
        teacher_assignment_read_model=teacher_assignment_read,
    )

    grade = factory.create_grade(
        student_id=str(student_id),
        subject_id=str(subject_id),
        score=92.5,
        type="assignment",
        teacher_id=str(teacher_id),
        class_id=None,
        term=None,
    )

    assert isinstance(grade, GradeRecord)
    assert grade.class_id is None
    assert grade.subject_id == subject_id
    assert grade.type == GradeType.ASSIGNMENT

    assert subject_read.calls == [subject_id]
    assert class_read.calls == []
    assert enrollment_read.calls == []
    assert teacher_assignment_read.calls == []
def test_create_grade_raises_if_subject_not_found():
    (
        factory,
        student_id,
        subject_id,
        teacher_id,
        class_id,
        subject_read,
        class_read,
        enrollment_read,
        teacher_assignment_read,
    ) = _build_grade_factory(
        subject_exists=False,
        class_exists=True,
        teacher_can_grade=True,
        student_enrolled=True,
    )

    with pytest.raises(ValueError) as exc:
        factory.create_grade(
            student_id=student_id,
            subject_id=subject_id,
            score=70.0,
            type=GradeType.EXAM,
            teacher_id=teacher_id,
            class_id=class_id,
        )

    assert "Subject" in str(exc.value)


def test_create_grade_raises_if_teacher_cannot_grade():
    (
        factory,
        student_id,
        subject_id,
        teacher_id,
        class_id,
        subject_read,
        class_read,
        enrollment_read,
        teacher_assignment_read,
    ) = _build_grade_factory(
        subject_exists=True,
        class_exists=True,
        teacher_can_grade=False,  
        student_enrolled=True,
    )

    with pytest.raises(NotSubjectTeacherException) as exc:
        factory.create_grade(
            student_id=student_id,
            subject_id=subject_id,
            score=88.0,
            type=GradeType.EXAM,
            teacher_id=teacher_id,
            class_id=class_id,
        )

    err = exc.value
    assert err.error_code == "NOT_SUBJECT_TEACHER"

def test_create_grade_raises_if_student_not_enrolled():
    (
        factory,
        student_id,
        subject_id,
        teacher_id,
        class_id,
        subject_read,
        class_read,
        enrollment_read,
        teacher_assignment_read,
    ) = _build_grade_factory(
        subject_exists=True,
        class_exists=True,
        teacher_can_grade=True,
        student_enrolled=False,  
    )

    with pytest.raises(StudentNotEnrolledForSubjectException) as exc:
        factory.create_grade(
            student_id=student_id,
            subject_id=subject_id,
            score=88.0,
            type=GradeType.EXAM,
            teacher_id=teacher_id,
            class_id=class_id,
        )

    err = exc.value
    assert err.error_code == "STUDENT_NOT_ENROLLED_FOR_SUBJECT"