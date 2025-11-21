from datetime import datetime
from bson import ObjectId

from app.contexts.school.domain.subject import Subject
from app.contexts.school.mapper.subject_mapper import SubjectMapper


def test_to_domain_pass_through_when_given_subject_instance():
    subj = Subject(
        name="Math",
        code="MATH101",
        description="Mathematics",
        allowed_grade_levels=[1, 2, 3],
    )

    result = SubjectMapper.to_domain(subj)

    # should return the same object, not a new one
    assert result is subj


def test_to_domain_from_dict_with_full_fields():
    now = datetime(2025, 1, 1, 10, 0)
    subject_id = ObjectId()

    raw = {
        "_id": subject_id,
        "name": "Physics",
        "code": "PHYS101",
        "description": "Basic Physics",
        "allowed_grade_levels": [10, 9, 11],
        "is_active": False,
        "created_at": now,
        "updated_at": now,
    }

    subj = SubjectMapper.to_domain(raw)

    assert isinstance(subj, Subject)
    assert subj.id == subject_id
    # name and code are passed to domain, which also applies its own normalization
    assert subj.name == "Physics"
    assert subj.code == "PHYS101"
    assert subj.description == "Basic Physics"
    # domain normalizes grade levels (sorted, unique)
    assert subj.allowed_grade_levels == (9, 10, 11)
    assert subj.is_active is False
    assert subj.created_at == now
    assert subj.updated_at == now


def test_to_domain_uses_defaults_when_fields_missing():
    raw = {
        "name": "Chemistry",
        "code": "CHEM101",
        # no description, no allowed_grade_levels, no timestamps, no is_active
    }

    subj = SubjectMapper.to_domain(raw)

    assert subj.name == "Chemistry"
    assert subj.code == "CHEM101"
    assert subj.description is None
    # default empty list -> domain returns empty tuple
    assert subj.allowed_grade_levels == ()
    # is_active default True from domain
    assert subj.is_active is True
    assert subj.created_at is not None
    assert subj.updated_at is not None


def test_to_persistence_round_trip_core_fields():
    created_at = datetime(2025, 1, 2, 8, 0)
    updated_at = datetime(2025, 1, 2, 9, 0)

    subj = Subject(
        name="Biology",
        code="BIO101",
        description="Intro Biology",
        allowed_grade_levels=[7, 8],
        is_active=True,
        created_at=created_at,
        updated_at=updated_at,
    )

    data = SubjectMapper.to_persistence(subj)

    assert data["_id"] == subj.id
    assert data["name"] == "Biology"
    assert data["code"] == "BIO101"
    assert data["description"] == "Intro Biology"
    # stored as list
    assert data["allowed_grade_levels"] == [7, 8]
    assert data["is_active"] is True
    assert data["created_at"] == created_at
    assert data["updated_at"] == updated_at