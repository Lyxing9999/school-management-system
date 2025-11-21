import pytest
from datetime import datetime, time
from bson import ObjectId

from app.contexts.school.domain.schedule import ScheduleSlot, DayOfWeek
from app.contexts.school.errors.schedule_exceptions import (
    InvalidDayOfWeekException,
    InvalidScheduleTimeException,
    StartTimeAfterEndTimeException,
)


def test_schedule_slot_init_valid():
    class_id = ObjectId()
    teacher_id = ObjectId()
    start = time(9, 0)
    end = time(10, 0)

    slot = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=start,
        end_time=end,
        room="A101",
    )

    assert slot.id is not None
    assert slot.class_id == class_id
    assert slot.teacher_id == teacher_id
    assert slot.day_of_week == DayOfWeek.MONDAY
    assert slot.start_time == start
    assert slot.end_time == end
    assert slot.room == "A101"
    assert isinstance(slot.created_at, datetime)
    assert isinstance(slot.updated_at, datetime)


def test_schedule_slot_normalizes_ids_from_strings():
    class_id = ObjectId()
    teacher_id = ObjectId()
    start = time(9, 0)
    end = time(10, 0)

    slot = ScheduleSlot(
        class_id=str(class_id),
        teacher_id=str(teacher_id),
        day_of_week=DayOfWeek.TUESDAY,
        start_time=start,
        end_time=end,
    )

    assert slot.class_id == class_id
    assert slot.teacher_id == teacher_id
    assert isinstance(slot.class_id, ObjectId)
    assert isinstance(slot.teacher_id, ObjectId)


def test_invalid_day_of_week_raises():
    class_id = ObjectId()
    teacher_id = ObjectId()
    start = time(9, 0)
    end = time(10, 0)

    with pytest.raises(InvalidDayOfWeekException):
        ScheduleSlot(
            class_id=class_id,
            teacher_id=teacher_id,
            day_of_week=8,  # invalid int
            start_time=start,
            end_time=end,
        )


def test_invalid_time_type_raises_on_init():
    class_id = ObjectId()
    teacher_id = ObjectId()

    with pytest.raises(InvalidScheduleTimeException):
        ScheduleSlot(
            class_id=class_id,
            teacher_id=teacher_id,
            day_of_week=DayOfWeek.MONDAY,
            start_time="09:00",  # not datetime.time
            end_time=time(10, 0),
        )


def test_start_time_after_end_time_raises_on_init():
    class_id = ObjectId()
    teacher_id = ObjectId()

    with pytest.raises(StartTimeAfterEndTimeException):
        ScheduleSlot(
            class_id=class_id,
            teacher_id=teacher_id,
            day_of_week=DayOfWeek.MONDAY,
            start_time=time(10, 0),
            end_time=time(9, 0),
        )


def test_move_updates_day_times_and_timestamp():
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
    old_updated_at = slot.updated_at

    slot.move(
        new_day_of_week=DayOfWeek.WEDNESDAY,
        new_start=time(13, 0),
        new_end=time(14, 0),
    )

    assert slot.day_of_week == DayOfWeek.WEDNESDAY
    assert slot.start_time == time(13, 0)
    assert slot.end_time == time(14, 0)
    assert slot.updated_at > old_updated_at


def test_move_with_invalid_day_raises():
    class_id = ObjectId()
    teacher_id = ObjectId()
    slot = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    with pytest.raises(InvalidDayOfWeekException):
        slot.move(
            new_day_of_week=9,  # invalid
            new_start=time(10, 0),
            new_end=time(11, 0),
        )


def test_move_with_invalid_times_raises():
    class_id = ObjectId()
    teacher_id = ObjectId()
    slot = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    with pytest.raises(StartTimeAfterEndTimeException):
        slot.move(
            new_day_of_week=DayOfWeek.MONDAY,
            new_start=time(11, 0),
            new_end=time(10, 0),
        )


def test_overlaps_false_when_different_days():
    class_id = ObjectId()
    teacher_id = ObjectId()

    slot1 = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    slot2 = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.TUESDAY,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )

    assert not slot1.overlaps(slot2)
    assert not slot2.overlaps(slot1)


def test_overlaps_false_when_back_to_back():
    class_id = ObjectId()
    teacher_id = ObjectId()

    slot1 = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    slot2 = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(10, 0),
        end_time=time(11, 0),
    )

    assert not slot1.overlaps(slot2)
    assert not slot2.overlaps(slot1)


def test_overlaps_true_on_partial_overlap():
    class_id = ObjectId()
    teacher_id = ObjectId()

    slot1 = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    slot2 = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 30),
        end_time=time(10, 30),
    )

    assert slot1.overlaps(slot2)
    assert slot2.overlaps(slot1)


def test_overlaps_true_on_full_containment():
    class_id = ObjectId()
    teacher_id = ObjectId()

    slot1 = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(9, 0),
        end_time=time(12, 0),
    )
    slot2 = ScheduleSlot(
        class_id=class_id,
        teacher_id=teacher_id,
        day_of_week=DayOfWeek.MONDAY,
        start_time=time(10, 0),
        end_time=time(11, 0),
    )

    assert slot1.overlaps(slot2)
    assert slot2.overlaps(slot1)