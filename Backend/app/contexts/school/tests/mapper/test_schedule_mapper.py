import pytest
from datetime import datetime, time
from bson import ObjectId

from app.contexts.school.domain.schedule import ScheduleSlot, DayOfWeek
from app.contexts.school.mapper.schedule_mapper import ScheduleMapper


def test_to_domain_pass_through_when_given_schedule_slot():
    """If we pass a ScheduleSlot instance, mapper should just return it."""
    class_id = ObjectId()
    teacher_id = ObjectId()
    slot = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(10, 0),
        room="A101",
    )

    result = ScheduleMapper.to_domain(slot)

    # same object, not a copy
    assert result is slot


def test_to_persistence_basic_fields():
    """ScheduleSlot -> dict has correct types/format."""
    class_id = ObjectId()
    teacher_id = ObjectId()
    start = time(9, 5)
    end = time(10, 30)

    slot = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.WEDNESDAY,
        start_time=start,
        end_time=end,
        room="B202",
    )

    data = ScheduleMapper.to_persistence(slot)

    assert data["_id"] == slot.id
    assert data["class_id"] == class_id
    assert data["teacher_id"] == teacher_id
    # day_of_week stored as int
    assert data["day_of_week"] == int(DayOfWeek.WEDNESDAY)
    # times stored as "HH:MM" strings
    assert data["start_time"] == "09:05"
    assert data["end_time"] == "10:30"
    assert data["room"] == "B202"
    assert data["created_at"] == slot.created_at
    assert data["updated_at"] == slot.updated_at


def test_to_domain_parses_string_times_and_int_day():
    """Dict with string times and int day -> proper ScheduleSlot."""
    class_id = ObjectId()
    teacher_id = ObjectId()
    created_at = datetime(2025, 1, 1, 8, 0)
    updated_at = datetime(2025, 1, 1, 9, 0)

    raw = {
        "_id": ObjectId(),
        "class_id": class_id,
        "teacher_id": teacher_id,
        "day_of_week": 3,              # WEDNESDAY
        "start_time": "09:15",
        "end_time": "10:45",
        "room": "C303",
        "created_at": created_at,
        "updated_at": updated_at,
    }

    slot = ScheduleMapper.to_domain(raw)

    assert isinstance(slot, ScheduleSlot)
    assert slot.id == raw["_id"]
    assert slot.class_id == class_id
    assert slot.teacher_id == teacher_id
    assert slot.day_of_week == DayOfWeek.WEDNESDAY
    assert slot.start_time == time(9, 15)
    assert slot.end_time == time(10, 45)
    assert slot.room == "C303"
    assert slot.created_at == created_at
    assert slot.updated_at == updated_at


def test_round_trip_schedule_slot_through_mapper():
    """ScheduleSlot -> dict -> ScheduleSlot keeps core fields consistent."""
    class_id = ObjectId()
    teacher_id = ObjectId()
    created_at = datetime(2025, 1, 2, 7, 0)
    updated_at = datetime(2025, 1, 2, 8, 0)

    original = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.FRIDAY,
        start_time=time(14, 0),
        end_time=time(15, 30),
        room="D404",
        created_at=created_at,
        updated_at=updated_at,
    )

    persisted = ScheduleMapper.to_persistence(original)
    restored = ScheduleMapper.to_domain(persisted)

    assert isinstance(restored, ScheduleSlot)
    assert restored.id == original.id
    assert restored.class_id == original.class_id
    assert restored.teacher_id == original.teacher_id
    assert restored.day_of_week == original.day_of_week
    assert restored.start_time == original.start_time
    assert restored.end_time == original.end_time
    assert restored.room == original.room
    assert restored.created_at == original.created_at
    assert restored.updated_at == original.updated_at