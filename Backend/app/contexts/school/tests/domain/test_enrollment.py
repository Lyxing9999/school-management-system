import pytest
from datetime import datetime
from bson import ObjectId

from app.contexts.school.domain.enrollment import Enrollment, EnrollmentStatus
from app.contexts.school.errors.enrollment_exceptions import (
    InvalidEnrollmentStatusException,
    EnrollmentAlreadyCompletedException,
    EnrollmentAlreadyDroppedException,
)


def test_enrollment_init_with_enum_status():
    student_id = ObjectId()
    class_id = ObjectId()

    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status=EnrollmentStatus.ACTIVE,
    )

    assert enrollment.id is not None
    assert enrollment.student_id == student_id
    assert enrollment.class_id == class_id
    assert enrollment.status == EnrollmentStatus.ACTIVE
    assert isinstance(enrollment.enrolled_at, datetime)
    assert isinstance(enrollment.created_at, datetime)
    assert isinstance(enrollment.updated_at, datetime)
    assert enrollment.dropped_at is None
    assert enrollment.completed_at is None


def test_enrollment_init_with_string_status():
    student_id = ObjectId()
    class_id = ObjectId()

    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status="completed",  # string
    )

    assert enrollment.status == EnrollmentStatus.COMPLETED


def test_enrollment_invalid_status_raises():
    student_id = ObjectId()
    class_id = ObjectId()

    with pytest.raises(InvalidEnrollmentStatusException):
        Enrollment(
            student_id=student_id,
            class_id=class_id,
            status="invalid-status",
        )


def test_ids_are_normalized_from_strings():
    student_id = ObjectId()
    class_id = ObjectId()

    enrollment = Enrollment(
        student_id=str(student_id),
        class_id=str(class_id),
        status=EnrollmentStatus.ACTIVE,
    )

    assert isinstance(enrollment.student_id, ObjectId)
    assert isinstance(enrollment.class_id, ObjectId)
    assert enrollment.student_id == student_id
    assert enrollment.class_id == class_id


def test_mark_dropped_from_active_sets_status_and_dropped_at():
    student_id = ObjectId()
    class_id = ObjectId()
    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status=EnrollmentStatus.ACTIVE,
    )
    old_updated_at = enrollment.updated_at

    enrollment.mark_dropped()

    assert enrollment.status == EnrollmentStatus.DROPPED
    assert isinstance(enrollment.dropped_at, datetime)
    assert enrollment.completed_at is None
    assert enrollment.updated_at > old_updated_at


def test_mark_dropped_when_already_dropped_raises():
    student_id = ObjectId()
    class_id = ObjectId()
    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status=EnrollmentStatus.DROPPED,
    )

    with pytest.raises(EnrollmentAlreadyDroppedException):
        enrollment.mark_dropped()


def test_mark_dropped_when_completed_raises():
    student_id = ObjectId()
    class_id = ObjectId()
    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status=EnrollmentStatus.COMPLETED,
    )

    with pytest.raises(EnrollmentAlreadyCompletedException):
        enrollment.mark_dropped()


def test_mark_completed_from_active_sets_status_and_completed_at():
    student_id = ObjectId()
    class_id = ObjectId()
    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status=EnrollmentStatus.ACTIVE,
    )
    old_updated_at = enrollment.updated_at

    enrollment.mark_completed()

    assert enrollment.status == EnrollmentStatus.COMPLETED
    assert isinstance(enrollment.completed_at, datetime)
    assert enrollment.dropped_at is None
    assert enrollment.updated_at > old_updated_at


def test_mark_completed_when_already_completed_raises():
    student_id = ObjectId()
    class_id = ObjectId()
    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status=EnrollmentStatus.COMPLETED,
    )

    with pytest.raises(EnrollmentAlreadyCompletedException):
        enrollment.mark_completed()


def test_mark_completed_when_dropped_raises():
    student_id = ObjectId()
    class_id = ObjectId()
    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status=EnrollmentStatus.DROPPED,
    )

    with pytest.raises(EnrollmentAlreadyDroppedException):
        enrollment.mark_completed()