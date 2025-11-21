# app/contexts/school/tests/mapper/test_class_section_mapper.py
import pytest
from datetime import datetime
from bson import ObjectId

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.mapper.class_mapper import ClassSectionMapper


def test_to_domain_from_dict_full_data():
    cls_id = ObjectId()
    teacher_id = ObjectId()
    s1, s2 = ObjectId(), ObjectId()
    subj1, subj2 = ObjectId(), ObjectId()
    now = datetime.utcnow()

    data = {
        "_id": cls_id,
        "name": "Grade 1A",
        "teacher_id": teacher_id,
        "student_ids": [s1, s2],
        "subject_ids": [subj1, subj2],
        "max_students": 30,
        "created_at": now,
        "updated_at": now,
        "deleted": False,
    }

    domain = ClassSectionMapper.to_domain(data)

    assert isinstance(domain, ClassSection)
    assert domain.id == cls_id
    assert domain.name == "Grade 1A"
    assert domain.teacher_id == teacher_id
    assert list(domain.student_ids) == [s1, s2]
    assert list(domain.subject_ids) == [subj1, subj2]
    assert domain.max_students == 30
    assert domain.created_at == now
    assert domain.updated_at == now
    assert domain.deleted is False


def test_to_domain_from_dict_with_missing_optionals_uses_defaults():
    data = {
        "_id": ObjectId(),
        "name": "Grade 2B",
        # no teacher_id, student_ids, subject_ids, max_students, deleted
        # created_at / updated_at also omitted
    }

    domain = ClassSectionMapper.to_domain(data)

    assert domain.name == "Grade 2B"
    assert domain.teacher_id is None
    assert domain.student_ids == ()
    assert domain.subject_ids == ()
    assert domain.max_students is None
    # created_at/updated_at set by domain constructor
    assert isinstance(domain.created_at, datetime)
    assert isinstance(domain.updated_at, datetime)
    assert domain.deleted is False


def test_to_domain_when_input_is_already_domain_returns_same_instance():
    original = ClassSection(name="Grade 3C")
    result = ClassSectionMapper.to_domain(original)

    assert result is original


def test_to_persistence_round_trip():
    teacher_id = ObjectId()
    s1, s2 = ObjectId(), ObjectId()
    subj1 = ObjectId()

    # Build a domain object
    cls = ClassSection(
        name="Grade 4D",
        teacher_id=teacher_id,
        student_ids=[s1, s2],
        subject_ids=[subj1],
        max_students=40,
    )

    # Domain -> dict
    data = ClassSectionMapper.to_persistence(cls)
    assert data["_id"] == cls.id
    assert data["name"] == cls.name
    assert data["teacher_id"] == teacher_id
    assert data["student_ids"] == [s1, s2]
    assert data["subject_ids"] == [subj1]
    assert data["max_students"] == 40
    assert data["deleted"] == cls.deleted

    # dict -> domain
    restored = ClassSectionMapper.to_domain(data)

    assert restored.id == cls.id
    assert restored.name == cls.name
    assert restored.teacher_id == cls.teacher_id
    assert list(restored.student_ids) == list(cls.student_ids)
    assert list(restored.subject_ids) == list(cls.subject_ids)
    assert restored.max_students == cls.max_students
    assert restored.deleted == cls.deleted