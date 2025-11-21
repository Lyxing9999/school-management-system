import pytest
from datetime import datetime, timedelta
from bson import ObjectId

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.errors.class_exceptions import (
    InvalidClassSectionNameError,
    StudentCapacityExceededError,
    InvalidMaxStudentsError,
    DuplicateStudentEnrollmentError,
    InvalidSubjectIdError,
    InvalidTeacherIdError,
)

def test_init_valid_class_section():
    section = ClassSection(name=" Grade 1A ")
    assert section.name == "Grade 1A"
    assert isinstance(section.id, ObjectId)
    assert section.teacher_id is None
    assert section.student_ids == ()
    assert section.subject_ids == ()
    assert section.max_students is None
    assert section.deleted is False
    assert isinstance(section.created_at, datetime)
    assert isinstance(section.updated_at, datetime)


def test_init_invalid_empty_name_raises():
    with pytest.raises(InvalidClassSectionNameError):
        ClassSection(name="   ")

def test_init_valid_class_section():
    section = ClassSection(name=" Grade 1A ")
    assert section.name == "Grade 1A"
    assert isinstance(section.id, ObjectId)
    assert section.teacher_id is None
    assert section.student_ids == ()
    assert section.subject_ids == ()
    assert section.max_students is None
    assert section.deleted is False
    assert isinstance(section.created_at, datetime)
    assert isinstance(section.updated_at, datetime)

def test_set_max_students_invalid_raises():
    section = ClassSection(name="A1")

    with pytest.raises(InvalidMaxStudentsError):
        section.set_max_students(0)

    with pytest.raises(InvalidMaxStudentsError):
        section.set_max_students(-5)

def test_init_invalid_empty_name_raises():
    with pytest.raises(InvalidClassSectionNameError):
        ClassSection(name="   ")
    
def test_rename_success():
    section = ClassSection(name="Old")
    old_updated_at = section.updated_at

    section.rename(" New Name ")

    assert section.name == "New Name"
    assert section.updated_at > old_updated_at

def test_rename_invalid_raises():
    section = ClassSection(name="Old")
    with pytest.raises(InvalidClassSectionNameError):
        section.rename("   ")

def test_rename_success():
    section = ClassSection(name="Old")
    old_updated_at = section.updated_at

    section.rename(" New Name ")

    assert section.name == "New Name"
    assert section.updated_at > old_updated_at

def test_rename_invalid_raises():
    section = ClassSection(name="Old")
    with pytest.raises(InvalidClassSectionNameError):

        section.rename("   ")
def test_rename_success():
    section = ClassSection(name="Old")
    old_updated_at = section.updated_at

    section.rename(" New Name ")

    assert section.name == "New Name"
    assert section.updated_at > old_updated_at

def test_rename_invalid_raises():
    section = ClassSection(name="Old")
    with pytest.raises(InvalidClassSectionNameError):
        section.rename("   ")

def test_assign_teacher_success():
    section = ClassSection(name="A1")
    teacher_id = ObjectId()

    section.assign_teacher(teacher_id)

    assert section.teacher_id == teacher_id


def test_assign_teacher_invalid_type_raises():
    section = ClassSection(name="A1")
    with pytest.raises(InvalidTeacherIdError):
        section.assign_teacher("not-an-object-id")  # type: ignore

def test_remove_teacher_sets_none():
    teacher_id = ObjectId()
    section = ClassSection(name="A1", teacher_id=teacher_id)

    section.remove_teacher()

    assert section.teacher_id is None

def test_enroll_student_success():
    section = ClassSection(name="A1", max_students=2)
    student_id = ObjectId()
    old_updated_at = section.updated_at

    section.enroll_student(student_id)

    assert student_id in section.student_ids
    assert len(section.student_ids) == 1
    assert section.updated_at > old_updated_at


def test_enroll_student_invalid_type_raises():
    section = ClassSection(name="A1", max_students=2)
    with pytest.raises(InvalidTeacherIdError):
        section.enroll_student("not-object-id")  # type: ignore


def test_enroll_student_duplicate_raises():
    student_id = ObjectId()
    section = ClassSection(name="A1", max_students=3, student_ids=[student_id])

    with pytest.raises(DuplicateStudentEnrollmentError):
        section.enroll_student(student_id)


def test_enroll_student_over_capacity_raises():
    s1, s2 = ObjectId(), ObjectId()
    section = ClassSection(name="A1", max_students=2, student_ids=[s1, s2])

    with pytest.raises(StudentCapacityExceededError):
        section.enroll_student(ObjectId())


def test_unenroll_student_success():
    s1, s2 = ObjectId(), ObjectId()
    section = ClassSection(name="A1", student_ids=[s1, s2])
    old_count = len(section.student_ids)

    section.unenroll_student(s1)

    assert s1 not in section.student_ids
    assert len(section.student_ids) == old_count - 1


def test_unenroll_student_invalid_type_raises():
    section = ClassSection(name="A1")
    with pytest.raises(InvalidTeacherIdError):
        section.unenroll_student("not-object-id")  # type: ignore


def test_unenroll_student_not_present_no_error():
    # should just do nothing
    s1, s2 = ObjectId(), ObjectId()
    section = ClassSection(name="A1", student_ids=[s1])

    section.unenroll_student(s2)  # no exception

    assert section.student_ids == (s1,)

def test_add_subject_success():
    section = ClassSection(name="A1")
    subj = ObjectId()
    section.add_subject(subj)

    assert subj in section.subject_ids


def test_add_subject_invalid_type_raises():
    section = ClassSection(name="A1")
    with pytest.raises(InvalidSubjectIdError):
        section.add_subject("not-object-id")  # type: ignore


def test_add_subject_ignores_duplicates():
    subj = ObjectId()
    section = ClassSection(name="A1", subject_ids=[subj])

    section.add_subject(subj)

    assert section.subject_ids.count(subj) == 1


def test_remove_subject_success():
    subj1, subj2 = ObjectId(), ObjectId()
    section = ClassSection(name="A1", subject_ids=[subj1, subj2])

    section.remove_subject(subj1)

    assert subj1 not in section.subject_ids
    assert subj2 in section.subject_ids


def test_remove_subject_invalid_type_raises():
    section = ClassSection(name="A1")
    with pytest.raises(InvalidSubjectIdError):
        section.remove_subject("not-object-id")  # type: ignore


def test_remove_subject_not_present_no_error():
    subj1, subj2 = ObjectId(), ObjectId()
    section = ClassSection(name="A1", subject_ids=[subj1])

    section.remove_subject(subj2)  # no exception

    assert section.subject_ids == (subj1,)

def test_soft_delete_sets_flag_and_updates_timestamp():
    section = ClassSection(name="A1")
    old_updated_at = section.updated_at

    section.soft_delete()

    assert section.deleted is True
    assert section.updated_at > old_updated_at