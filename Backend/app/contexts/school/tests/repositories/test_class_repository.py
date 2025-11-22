import pytest
from bson import ObjectId

from app.contexts.school.domain.class_section import ClassSection
from app.contexts.school.mapper.class_mapper import ClassSectionMapper
from app.contexts.school.repositories.class_repository import (
    MongoClassSectionRepository,
)


class FakeResult:
    def __init__(self, matched_count: int = 0, inserted_id=None):
        self.matched_count = matched_count
        self.inserted_id = inserted_id


class FakeCollection:
    def __init__(self):
        self.docs = []

    def _match(self, doc: dict, filter_: dict) -> bool:
        for key, value in filter_.items():
            if isinstance(value, dict) and "$ne" in value:
                if doc.get(key) == value["$ne"]:
                    return False
            else:
                if doc.get(key) != value:
                    return False
        return True

    def insert_one(self, doc: dict) -> FakeResult:
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        stored = dict(doc)
        self.docs.append(stored)
        return FakeResult(inserted_id=stored["_id"])

    def find_one(self, filter_: dict) -> dict | None:
        for doc in self.docs:
            if self._match(doc, filter_):
                return dict(doc)
        return None

    def update_one(self, filter_: dict, update: dict) -> FakeResult:
        for i, doc in enumerate(self.docs):
            if self._match(doc, filter_):
                if "$set" in update:
                    for k, v in update["$set"].items():
                        self.docs[i][k] = v
                return FakeResult(matched_count=1)
        return FakeResult(matched_count=0)


@pytest.fixture
def fake_collection():
    return FakeCollection()


@pytest.fixture
def class_mapper():
    return ClassSectionMapper()


@pytest.fixture
def repo(fake_collection, class_mapper):
    return MongoClassSectionRepository(collection=fake_collection, mapper=class_mapper)


def test_insert_persists_document_and_returns_section(repo, fake_collection):
    section = ClassSection(name="Grade 1A")

    returned = repo.insert(section)

    assert returned is section
    assert len(fake_collection.docs) == 1
    stored = fake_collection.docs[0]
    assert stored["_id"] == section.id
    assert stored["name"] == "Grade 1A"
    assert stored["deleted"] is False


def test_find_by_id_returns_domain_object(repo, fake_collection, class_mapper):
    section = ClassSection(name="Grade 2B")
    fake_collection.insert_one(class_mapper.to_persistence(section))

    found = repo.find_by_id(section.id)

    assert isinstance(found, ClassSection)
    assert found.id == section.id
    assert found.name == "Grade 2B"


def test_find_by_id_returns_none_when_not_found(repo):
    not_existing_id = ObjectId()

    found = repo.find_by_id(not_existing_id)

    assert found is None


def test_find_by_id_ignores_soft_deleted(repo, fake_collection, class_mapper):
    section = ClassSection(name="Grade 3C")
    doc = class_mapper.to_persistence(section)
    doc["deleted"] = True
    fake_collection.insert_one(doc)

    found = repo.find_by_id(section.id)

    assert found is None


def test_find_by_name_returns_domain_object(repo, fake_collection, class_mapper):
    section = ClassSection(name="Grade 4D")
    fake_collection.insert_one(class_mapper.to_persistence(section))

    found = repo.find_by_name("Grade 4D")

    assert isinstance(found, ClassSection)
    assert found.id == section.id
    assert found.name == "Grade 4D"


def test_find_by_name_returns_none_when_not_found(repo):
    found = repo.find_by_name("Non Existing Class")
    assert found is None


def test_soft_delete_sets_deleted_flag_and_returns_true(repo, fake_collection, class_mapper):
    section = ClassSection(name="Grade 5E")
    fake_collection.insert_one(class_mapper.to_persistence(section))

    result = repo.soft_delete(section.id)

    assert result is True
    stored = fake_collection.find_one({"_id": section.id})
    assert stored["deleted"] is True


def test_soft_delete_returns_false_if_no_document(repo, fake_collection):
    not_existing_id = ObjectId()

    result = repo.soft_delete(not_existing_id)

    assert result is False
    assert fake_collection.docs == []


def test_update_returns_updated_section_when_match_found(repo, fake_collection, class_mapper):
    section = ClassSection(name="Old Name")
    fake_collection.insert_one(class_mapper.to_persistence(section))

    section.rename("New Name")

    updated = repo.update(section)

    assert updated is section
    stored = fake_collection.find_one({"_id": section.id})
    assert stored["name"] == "New Name"


def test_update_returns_none_when_no_matching_document(repo):
    section = ClassSection(name="Orphan Class")

    updated = repo.update(section)

    assert updated is None