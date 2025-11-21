import pytest

from app.contexts.school.domain.subject import Subject
from app.contexts.school.factory.subject_factory import SubjectFactory
from app.contexts.school.errors.subject_exceptions import (
    SubjectCodeAlreadyExistsException,
    SubjectNameAlreadyExistsException,
)


class FakeSubjectReadModel:
    """
    Very small in-memory fake for subject_read_model.
    """

    def __init__(self):
        # store by normalized code/name
        self._by_code = {}
        self._by_name = {}

    def add_subject(self, name: str, code: str):
        normalized_name = name.strip()
        normalized_code = code.strip().upper()
        doc = {"name": normalized_name, "code": normalized_code}
        self._by_code[normalized_code] = doc
        self._by_name[normalized_name] = doc

    def get_by_code(self, code: str):
        return self._by_code.get(code)

    def get_by_name(self, name: str):
        return self._by_name.get(name)


def _build_factory_with_seed(
    existing_by_code: dict[str, str] | None = None,
    existing_by_name: dict[str, str] | None = None,
) -> SubjectFactory:
    """
    Helper to build a factory with some existing subjects registered
    by code or name.
    """
    fake = FakeSubjectReadModel()
    existing_by_code = existing_by_code or {}
    existing_by_name = existing_by_name or {}

    # seed by code
    for code, name in existing_by_code.items():
        fake.add_subject(name=name, code=code)

    # seed by name (if not already added)
    for name, code in existing_by_name.items():
        fake.add_subject(name=name, code=code)

    return SubjectFactory(fake)


def test_create_subject_success_normalizes_name_and_code():
    read_model = FakeSubjectReadModel()
    factory = SubjectFactory(read_model)

    subject = factory.create_subject(
        name="   mathematics ",
        code="  math101 ",
        description="Basic Mathematics",
        allowed_grade_levels=[1, 3, 2, 3],  # duplicates and unsorted on purpose
    )

    assert isinstance(subject, Subject)
    # name trimmed
    assert subject.name == "mathematics"
    # code upper-cased and trimmed
    assert subject.code == "MATH101"
    # description set
    assert subject.description == "Basic Mathematics"
    # grade levels normalized (sorted, unique) by domain
    assert subject.allowed_grade_levels == (1, 2, 3)
    # is_active default True
    assert subject.is_active is True


def test_create_subject_raises_if_code_already_exists():
    existing_code = "MATH101"
    # Pre-seed read model so that this code exists
    factory = _build_factory_with_seed(existing_by_code={existing_code: "Mathematics"})

    with pytest.raises(SubjectCodeAlreadyExistsException) as exc:
        factory.create_subject(
            name="Something Else",
            code="  math101  ",  # same code in different case/spacing
            description=None,
        )

    assert existing_code in exc.value.message or "math101" in exc.value.message.lower()


def test_create_subject_raises_if_name_already_exists():
    existing_name = "Mathematics"
    # Pre-seed read model so that this name exists
    factory = _build_factory_with_seed(existing_by_name={existing_name: "MATH101"})

    with pytest.raises(SubjectNameAlreadyExistsException) as exc:
        factory.create_subject(
            name="  Mathematics  ",  # same name with spaces
            code="MATH102",
            description=None,
        )

    assert "Mathematics" in exc.value.message