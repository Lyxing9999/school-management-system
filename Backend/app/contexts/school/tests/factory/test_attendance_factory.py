import pytest
from datetime import date
from bson import ObjectId

from app.contexts.school.domain.attendance import AttendanceRecord, AttendanceStatus
from app.contexts.school.factory.attendance_factory import AttendanceFactory
from app.contexts.school.errors.attendance_exceptions import (
    NotClassTeacherException,
    StudentNotEnrolledInClassException,
    AttendanceAlreadyMarkedException,
)

# ------------ Fake read models -----------------


class FakeClassReadModel:
    def __init__(self, class_doc):
        # class_doc is a dict or None
        self.class_doc = class_doc
        self.calls = []

    def get_by_id(self, class_id: ObjectId):
        self.calls.append(class_id)
        return self.class_doc


# class FakeEnrollmentReadModel:
#     def __init__(self, enrolled: bool):
#         self.enrolled = enrolled
#         self.calls = []

    # def is_student_enrolled(self, student_id: ObjectId, class_id: ObjectId) -> bool:
    #     self.calls.append((student_id, class_id))
    #     return self.enrolled


class FakeAttendanceReadModel:
    def __init__(self, already_exists: bool):
        self.already_exists = already_exists
        self.calls = []

    def get_by_student_class_date(
        self,
        student_id: ObjectId,
        class_id: ObjectId,
        record_date: date | None,
    ):
        self.calls.append((student_id, class_id, record_date))
        if self.already_exists:
            return {"_id": ObjectId()}
        return None


def test_create_record_success():
    student_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()

    class_doc = {
        "_id": class_id,
        "teacher_id": teacher_id,  # ✅ correct teacher
    }

    factory = AttendanceFactory(
        class_read_model=FakeClassReadModel(class_doc),
        # enrollment_read_model=FakeEnrollmentReadModel(enrolled=True),
        attendance_read_model=FakeAttendanceReadModel(already_exists=False),
    )

    record = factory.create_record(
        student_id=student_id,
        class_id=class_id,
        status=AttendanceStatus.PRESENT,
        teacher_id=teacher_id,
        record_date=None,  # let domain default to today
    )

    assert isinstance(record, AttendanceRecord)
    assert record.student_id == student_id
    assert record.class_id == class_id
    assert record.marked_by_teacher_id == teacher_id
    assert record.status == AttendanceStatus.PRESENT


def test_create_record_raises_when_not_class_teacher():
    student_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()         
    different_teacher = ObjectId()   

    class_doc = {
        "_id": class_id,
        "teacher_id": different_teacher,  # mismatch
    }

    factory = AttendanceFactory(
        class_read_model=FakeClassReadModel(class_doc),
        # enrollment_read_model=FakeEnrollmentReadModel(enrolled=True),
        attendance_read_model=FakeAttendanceReadModel(already_exists=False),
    )

    with pytest.raises(NotClassTeacherException):
        factory.create_record(
            student_id=student_id,
            class_id=class_id,
            status="present",
            teacher_id=teacher_id,
            record_date=None,
        )


def test_create_record_raises_when_student_not_enrolled():
    student_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()

    class_doc = {
        "_id": class_id,
        "teacher_id": teacher_id,  
    }

    factory = AttendanceFactory(
        class_read_model=FakeClassReadModel(class_doc),
        # enrollment_read_model=FakeEnrollmentReadModel(enrolled=False), 
        attendance_read_model=FakeAttendanceReadModel(already_exists=False),
    )

    with pytest.raises(StudentNotEnrolledInClassException):
        factory.create_record(
            student_id=student_id,
            class_id=class_id,
            status=AttendanceStatus.ABSENT,
            teacher_id=teacher_id,
            record_date=None,
        )


def test_create_record_raises_when_already_marked():
    student_id = ObjectId()
    class_id = ObjectId()
    teacher_id = ObjectId()

    class_doc = {
        "_id": class_id,
        "teacher_id": teacher_id,
    }

    factory = AttendanceFactory(
        class_read_model=FakeClassReadModel(class_doc),
        # enrollment_read_model=FakeEnrollmentReadModel(enrolled=True),
        attendance_read_model=FakeAttendanceReadModel(already_exists=True),  
    )

    with pytest.raises(AttendanceAlreadyMarkedException):
        factory.create_record(
            student_id=student_id,
            class_id=class_id,
            status=AttendanceStatus.EXCUSED,
            teacher_id=teacher_id,
            record_date=None,
        )