# app/contexts/school/tests/domain/test_subject.py

import pytest
from datetime import datetime
from bson import ObjectId

from app.contexts.school.domain.subject import Subject
from app.contexts.school.errors.subject_exceptions import (
    InvalidSubjectNameError,
    InvalidSubjectCodeError,
    InvalidGradeLevelError,
)


def test_subject_init_valid():
    subj = Subject(
        name="  Mathematics  ",
        code="  math101 ",
        description="Basic math",
        allowed_grade_levels=[1, 3, 2, 3],  # duplicates + unsorted
        is_active=True,
    )

    assert isinstance(subj.id, ObjectId)
    assert subj.name == "Mathematics"
    assert subj.code == "MATH101"  # uppercased + stripped
    assert subj.description == "Basic math"
    # normalized: unique + sorted
    assert subj.allowed_grade_levels == (1, 2, 3)
    assert subj.is_active is True
    assert isinstance(subj.created_at, datetime)
    assert isinstance(subj.updated_at, datetime)


def test_subject_init_invalid_empty_name_raises():
    with pytest.raises(InvalidSubjectNameError):
        Subject(
            name="   ",
            code="MATH101",
        )


def test_subject_init_invalid_empty_code_raises():
    with pytest.raises(InvalidSubjectCodeError):
        Subject(
            name="Mathematics",
            code="   ",
        )


def test_subject_init_invalid_grade_level_below_range_raises():
    with pytest.raises(InvalidGradeLevelError):
        Subject(
            name="Math",
            code="MATH101",
            allowed_grade_levels=[0, 1],  # 0 invalid
        )


def test_subject_init_invalid_grade_level_above_range_raises():
    with pytest.raises(InvalidGradeLevelError):
        Subject(
            name="Math",
            code="MATH101",
            allowed_grade_levels=[1, 13],  # 13 invalid
        )


def test_rename_success_updates_name_and_timestamp():
    subj = Subject(name="Old name", code="CODE1")
    old_updated_at = subj.updated_at

    subj.rename("  New Name  ")

    assert subj.name == "New Name"
    assert subj.updated_at > old_updated_at


def test_rename_invalid_empty_raises():
    subj = Subject(name="Old name", code="CODE1")

    with pytest.raises(InvalidSubjectNameError):
        subj.rename("   ")


def test_change_code_success_uppercases_and_updates_timestamp():
    subj = Subject(name="Math", code="MATH1")
    old_updated_at = subj.updated_at

    subj.change_code("  math2 ")

    assert subj.code == "MATH2"
    assert subj.updated_at > old_updated_at


def test_change_code_invalid_empty_raises():
    subj = Subject(name="Math", code="MATH1")

    with pytest.raises(InvalidSubjectCodeError):
        subj.change_code("   ")


def test_update_description_sets_value_and_timestamp():
    subj = Subject(name="Math", code="MATH1", description=None)
    old_updated_at = subj.updated_at

    subj.update_description("New description")

    assert subj.description == "New description"
    assert subj.updated_at > old_updated_at


def test_set_allowed_grade_levels_normalizes_and_updates_timestamp():
    subj = Subject(name="Math", code="MATH1", allowed_grade_levels=[1, 2])
    old_updated_at = subj.updated_at

    subj.set_allowed_grade_levels([5, 3, 4, 3])

    assert subj.allowed_grade_levels == (3, 4, 5)
    assert subj.updated_at > old_updated_at


def test_set_allowed_grade_levels_invalid_level_raises():
    subj = Subject(name="Math", code="MATH1", allowed_grade_levels=[1, 2])

    with pytest.raises(InvalidGradeLevelError):
        subj.set_allowed_grade_levels([1, 0])  # 0 invalid


def test_deactivate_sets_flag_and_updates_timestamp():
    subj = Subject(name="Math", code="MATH1", is_active=True)
    old_updated_at = subj.updated_at

    subj.deactivate()

    assert subj.is_active is False
    assert subj.updated_at > old_updated_at


def test_activate_sets_flag_and_updates_timestamp():
    subj = Subject(name="Math", code="MATH1", is_active=False)
    old_updated_at = subj.updated_at

    subj.activate()

    assert subj.is_active is True
    assert subj.updated_at > old_updated_at