import pytest
from bson import ObjectId

from app.contexts.school.read_models.class_read_model import ClassReadModel


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

    def find(self, filter_: dict | None = None):
        filter_ = filter_ or {}
        for doc in self.docs:
            if self._match(doc, filter_):
                yield dict(doc)


class FakeDB:
    """Minimal DB wrapper to mimic db['classes'] behaviour."""

    def __init__(self, collection: FakeCollection):
        self._collection = collection

    def __getitem__(self, name: str) -> FakeCollection:
        assert name == "classes"
        return self._collection


@pytest.fixture
def fake_collection():
    return FakeCollection()


@pytest.fixture
def read_model(fake_collection):
    db = FakeDB(fake_collection)
    return ClassReadModel(db)


def test_read_model_get_by_id_returns_raw_document(read_model, fake_collection):
    _id = ObjectId()
    fake_collection.insert_one(
        {
            "_id": _id,
            "name": "Grade 6A",
            "deleted": False,
        }
    )

    doc = read_model.get_by_id(_id)

    assert doc is not None
    assert doc["_id"] == _id
    assert doc["name"] == "Grade 6A"


def test_read_model_get_by_id_returns_none_for_deleted(read_model, fake_collection):
    _id = ObjectId()
    fake_collection.insert_one(
        {
            "_id": _id,
            "name": "Grade 6B",
            "deleted": True,
        }
    )

    doc = read_model.get_by_id(_id)

    assert doc is None


def test_read_model_get_by_name_returns_raw_document(read_model, fake_collection):
    fake_collection.insert_one(
        {
            "_id": ObjectId(),
            "name": "Grade 7A",
            "deleted": False,
        }
    )

    doc = read_model.get_by_name("Grade 7A")

    assert doc is not None
    assert doc["name"] == "Grade 7A"


def test_read_model_get_by_name_returns_none_when_not_found(read_model):
    doc = read_model.get_by_name("No Such Class")
    assert doc is None


def test_read_model_list_all_filters_deleted(read_model, fake_collection):
    fake_collection.insert_one(
        {"_id": ObjectId(), "name": "C1", "deleted": False}
    )
    fake_collection.insert_one(
        {"_id": ObjectId(), "name": "C2", "deleted": True}
    )
    fake_collection.insert_one(
        {"_id": ObjectId(), "name": "C3", "deleted": False}
    )

    docs = read_model.list_all()

    names = sorted(d["name"] for d in docs)
    assert names == ["C1", "C3"]