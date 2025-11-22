# app/contexts/school/tests/factory/test_class_factory.py

import pytest
from bson import ObjectId

from app.contexts.school.factory.class_factory import ClassFactory
from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.errors.class_exceptions import (
    ClassNameAlreadyExistsException,
    TeacherOverClassLoadException,
)


class FakeClassReadModel:
    def __init__(self, existing_names=None):
        # set of names that "already exist" in DB
        self.existing_names = set(existing_names or [])

    def get_by_name(self, name: str):
        return {"name": name} if name in self.existing_names else None


class FakeTeacherReadModel:
    def __init__(self, max_load_by_teacher=None, current_load_by_teacher=None):
        # dict[ObjectId, int]
        self.max_load_by_teacher = max_load_by_teacher or {}
        self.current_load_by_teacher = current_load_by_teacher or {}

    def get_max_class_load(self, teacher_id: ObjectId) -> int | None:
        return self.max_load_by_teacher.get(teacher_id)

    def count_classes_for_teacher(self, teacher_id: ObjectId) -> int:
        return self.current_load_by_teacher.get(teacher_id, 0)


def test_create_class_success_without_teacher():
    class_read = FakeClassReadModel()
    teacher_read = FakeTeacherReadModel()
    factory = ClassFactory(class_read_model=class_read, teacher_read_model=teacher_read)

    cls = factory.create_class(
        name="Grade 1A",
        teacher_id=None,
        subject_ids=[],
        max_students=30,
    )

    assert isinstance(cls, ClassSection)
    assert cls.name == "Grade 1A"
    assert cls.teacher_id is None
    assert cls.max_students == 30
    assert list(cls.subject_ids) == []


def test_create_class_name_already_exists_raises():
    class_read = FakeClassReadModel(existing_names={"Grade 1A"})
    teacher_read = FakeTeacherReadModel()
    factory = ClassFactory(class_read_model=class_read, teacher_read_model=teacher_read)

    with pytest.raises(ClassNameAlreadyExistsException):
        factory.create_class(
            name="Grade 1A",
            teacher_id=None,
            subject_ids=[],
            max_students=30,
        )


def test_create_class_normalizes_teacher_and_subject_ids_from_strings():
    teacher_id = ObjectId()
    subj1 = ObjectId()
    subj2 = ObjectId()

    class_read = FakeClassReadModel()
    teacher_read = FakeTeacherReadModel()
    factory = ClassFactory(class_read_model=class_read, teacher_read_model=teacher_read)

    cls = factory.create_class(
        name="Grade 2B",
        teacher_id=str(teacher_id),          
        subject_ids=[str(subj1), subj2],       
        max_students=35,
    )

    assert isinstance(cls, ClassSection)
    assert cls.teacher_id == teacher_id
    assert list(cls.subject_ids) == [subj1, subj2]


def test_create_class_teacher_over_class_load_raises():
    teacher_id = ObjectId()

    class_read = FakeClassReadModel()
    teacher_read = FakeTeacherReadModel(
        max_load_by_teacher={teacher_id: 2},
        current_load_by_teacher={teacher_id: 2},
    )
    factory = ClassFactory(class_read_model=class_read, teacher_read_model=teacher_read)

    with pytest.raises(TeacherOverClassLoadException):
        factory.create_class(
            name="Grade 3C",
            teacher_id=teacher_id,
            subject_ids=[],
            max_students=30,
        )


def test_create_class_when_max_load_is_none_allows_any_number_of_classes():
    """
    If get_max_class_load returns None, the factory should NOT enforce limits.
    """
    teacher_id = ObjectId()

    class_read = FakeClassReadModel()
    teacher_read = FakeTeacherReadModel(
        max_load_by_teacher={teacher_id: None},   # no limit
        current_load_by_teacher={teacher_id: 100} # many classes, but no max ⇒ allowed
    )
    factory = ClassFactory(class_read_model=class_read, teacher_read_model=teacher_read)

    cls = factory.create_class(
        name="Grade 4D",
        teacher_id=teacher_id,
        subject_ids=[],
        max_students=25,
    )

    assert isinstance(cls, ClassSection)
    assert cls.teacher_id == teacher_id
    assert cls.name == "Grade 4D"