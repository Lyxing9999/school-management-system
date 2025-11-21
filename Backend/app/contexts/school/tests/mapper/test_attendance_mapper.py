import pytest
from datetime import datetime, date
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.mapper.attendance_mapper import AttendanceMapper


def test_to_domain_from_dict_with_datetime_date():
    rec_id = ObjectId()
    student_id = ObjectId()
    class_id = ObjectId()
    raw_datetime = datetime(2025, 1, 1, 9, 0, 0)
    created_at = datetime(2025, 1, 1, 8, 0, 0)
    updated_at = datetime(2025, 1, 1, 8, 30, 0)

    data = {
        "_id": rec_id,
        "student_id": student_id,
        "class_id": class_id,
        "status": "present",
        "date": raw_datetime,  # datetime, should be converted to date
        "marked_by_teacher_id": ObjectId(),
        "created_at": created_at,
        "updated_at": updated_at,
    }

    record = AttendanceMapper.to_domain(data)

    assert isinstance(record, AttendanceRecord)
    assert record.id == rec_id
    assert record.student_id == student_id
    assert record.class_id == class_id
    assert record.status == AttendanceStatus.PRESENT
    assert record.date == raw_datetime.date()
    assert record.created_at == created_at
    assert record.updated_at == updated_at


def test_to_domain_from_dict_with_date_object():
    rec_id = ObjectId()
    student_id = ObjectId()
    class_id = ObjectId()
    record_date = date(2025, 2, 2)

    data = {
        "_id": rec_id,
        "student_id": student_id,
        "class_id": class_id,
        "status": AttendanceStatus.ABSENT,  # enum object
        "date": record_date,
        "marked_by_teacher_id": None,
    }

    record = AttendanceMapper.to_domain(data)

    assert record.id == rec_id
    assert record.date == record_date
    assert record.status == AttendanceStatus.ABSENT
    assert record.marked_by_teacher_id is None


def test_to_domain_from_dict_with_iso_string_date():
    rec_id = ObjectId()
    student_id = ObjectId()
    class_id = ObjectId()
    iso_str = "2025-03-10T09:00:00"
    parsed_date = datetime.fromisoformat(iso_str).date()

    data = {
        "_id": rec_id,
        "student_id": student_id,
        "class_id": class_id,
        "status": "excused",
        "date": iso_str,
    }

    record = AttendanceMapper.to_domain(data)

    assert record.id == rec_id
    assert record.date == parsed_date
    assert record.status == AttendanceStatus.EXCUSED


def test_to_domain_when_data_is_already_domain_returns_same_instance():
    student_id = ObjectId()
    class_id = ObjectId()

    original = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
    )

    result = AttendanceMapper.to_domain(original)

    assert result is original


def test_to_persistence_builds_correct_dict():
    student_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()
    record_date = date(2025, 4, 1)

    record = AttendanceRecord(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.ABSENT,
        record_date=record_date,
        marked_by_teacher_id=teacher_id,
    )

    data = AttendanceMapper.to_persistence(record)

    assert data["_id"] == record.id
    assert data["student_id"] == student_id
    assert data["class_id"] == class_id
    assert data["status"] == "absent"  # value of enum
    assert data["date"] == record_date
    assert data["marked_by_teacher_id"] == teacher_id
    assert data["created_at"] == record.created_at
    assert data["updated_at"] == record.updated_at


def test_round_trip_dict_to_domain_and_back():
    rec_id = ObjectId()
    student_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()
    record_date = date(2025, 5, 5)
    created_at = datetime(2025, 5, 5, 8, 0, 0)
    updated_at = datetime(2025, 5, 5, 9, 0, 0)

    data = {
        "_id": rec_id,
        "student_id": student_id,
        "class_id": class_id,
        "status": "present",
        "date": record_date,
        "marked_by_teacher_id": teacher_id,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    record = AttendanceMapper.to_domain(data)
    persisted = AttendanceMapper.to_persistence(record)

    assert persisted["_id"] == rec_id
    assert persisted["student_id"] == student_id
    assert persisted["class_id"] == class_id
    assert persisted["status"] == "present"
    assert persisted["date"] == record_date
    assert persisted["marked_by_teacher_id"] == teacher_id