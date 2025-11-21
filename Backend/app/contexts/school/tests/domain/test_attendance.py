import pytest
from datetime import datetime, timedelta, date
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.errors.attendance_exceptions import (
    InvalidAttendanceStatusException,
    AttendanceDateInFutureException,
)


def test_attendance_init_with_enum_status():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
    )

    assert record.id is not None
    assert record.student_id == student_id
    assert record.class_id == class_id
    assert record.status == AttendanceStatus.PRESENT
    assert isinstance(record.created_at, datetime)
    assert isinstance(record.updated_at, datetime)
    assert isinstance(record.date, date)


def test_attendance_init_with_string_status():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status="present",  
    )

    assert record.status == AttendanceStatus.PRESENT


def test_attendance_invalid_status_raises():
    student_id = ObjectId()
    class_id = ObjectId()

    with pytest.raises(InvalidAttendanceStatusException):
        AttendanceRecord(
            student_id=student_id,
            class_id=class_id,
            status="late", 
        )


def test_attendance_default_date_is_today():
    student_id = ObjectId()
    class_id = ObjectId()
    today = datetime.utcnow().date()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.ABSENT,
    )

    assert record.date == today


def test_attendance_date_in_future_raises():
    student_id = ObjectId()
    class_id = ObjectId()
    future_date = datetime.utcnow().date() + timedelta(days=1)

    with pytest.raises(AttendanceDateInFutureException):
        AttendanceRecord(
            student_id=student_id,
            class_id=class_id,
            status=AttendanceStatus.PRESENT,
            record_date=future_date,
        )


def test_change_status_updates_status_and_timestamp():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
    )
    old_updated_at = record.updated_at

    record.change_status(AttendanceStatus.ABSENT)

    assert record.status == AttendanceStatus.ABSENT
    assert record.updated_at > old_updated_at


import pytest
from datetime import datetime, timedelta, date
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.errors.attendance_exceptions import (
    InvalidAttendanceStatusException,
    AttendanceDateInFutureException,
)


def test_attendance_init_with_enum_status():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
    )

    assert record.id is not None
    assert record.student_id == student_id
    assert record.class_id == class_id
    assert record.status == AttendanceStatus.PRESENT
    assert isinstance(record.created_at, datetime)
    assert isinstance(record.updated_at, datetime)
    assert isinstance(record.date, date)


def test_attendance_init_with_string_status():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status="present",  
    )

    assert record.status == AttendanceStatus.PRESENT


def test_attendance_invalid_status_raises():
    student_id = ObjectId()
    class_id = ObjectId()

    with pytest.raises(InvalidAttendanceStatusException):
        AttendanceRecord(
            student_id=student_id,
            class_id=class_id,
            status="late", 
        )


def test_attendance_default_date_is_today():
    student_id = ObjectId()
    class_id = ObjectId()
    today = datetime.utcnow().date()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.ABSENT,
    )

    assert record.date == today


def test_attendance_date_in_future_raises():
    student_id = ObjectId()
    class_id = ObjectId()
    future_date = datetime.utcnow().date() + timedelta(days=1)

    with pytest.raises(AttendanceDateInFutureException):
        AttendanceRecord(
            student_id=student_id,
            class_id=class_id,
            status=AttendanceStatus.PRESENT,
            record_date=future_date,
        )


def test_change_status_updates_status_and_timestamp():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
    )
    old_updated_at = record.updated_at

    record.change_status(AttendanceStatus.ABSENT)

    assert record.status == AttendanceStatus.ABSENT
    assert record.updated_at > old_updated_at


def test_change_status_accepts_string_status():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
    )

    record.change_status("excused")

    assert record.status == AttendanceStatus.EXCUSED


def test_ids_are_normalized_from_strings():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=str(student_id), 
        class_id=str(class_id),
        status=AttendanceStatus.PRESENT,
    )

    assert isinstance(record.student_id, ObjectId)
    assert isinstance(record.class_id, ObjectId)
    assert record.student_id == student_id
    assert record.class_id == class_id


def test_marked_by_teacher_id_is_stored():
    student_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
        marked_by_teacher_id=teacher_id,
    )

    assert record.marked_by_teacher_id == teacher_id

def test_ids_are_normalized_from_strings():
    student_id = ObjectId()
    class_id = ObjectId()

    record = AttendanceRecord(
        student_id=str(student_id),  # pass as string
        class_id=str(class_id),
        status=AttendanceStatus.PRESENT,
    )

    assert isinstance(record.student_id, ObjectId)
    assert isinstance(record.class_id, ObjectId)
    assert record.student_id == student_id
    assert record.class_id == class_id


def test_marked_by_teacher_id_is_stored():
    student_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
        marked_by_teacher_id=teacher_id,
    )

    assert record.marked_by_teacher_id == teacher_id