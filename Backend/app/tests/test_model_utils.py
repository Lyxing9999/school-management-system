from app.utils.pyobjectid import PyObjectId
import pytest
from bson import ObjectId
from pydantic import BaseModel, Field
from app.utils.model_utils import default_model_utils
from app.error.exceptions import (
    BadRequestError, 
    PydanticBaseValidationError, 
    NotFoundError
)

class DummyModel(BaseModel):
    id: str = Field(alias="_id")
    other_field: str

    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True,
    }

class DummyCollection:
    def __init__(self, return_doc=True):
        self.return_doc = return_doc
        self.name = "dummy_collection"

    def find_one(self, query):
        if self.return_doc:
            return {"_id": query.get("_id"), "other_field": "value"}
        return None

@pytest.fixture
def model_utils():
    return default_model_utils

def test_validate_object_id_success_and_failure(model_utils):
    oid = ObjectId()
    assert model_utils.validate_object_id(str(oid)) == oid
    assert model_utils.validate_object_id(oid) == oid

    with pytest.raises(BadRequestError):
        model_utils.validate_object_id(None)
    with pytest.raises(BadRequestError):
        model_utils.validate_object_id(12345)
    with pytest.raises(BadRequestError):
        model_utils.validate_object_id("invalid_objectid_string")

def test_try_convert_object_id(model_utils):
    oid = ObjectId()
    assert model_utils.try_convert_object_id(str(oid)) == oid
    assert model_utils.try_convert_object_id(oid) == oid
    assert model_utils.try_convert_object_id(None) is None
    assert model_utils.try_convert_object_id("invalid") is None
    assert model_utils.try_convert_object_id(123) is None

def test_to_model_and_to_model_list_success_and_fail(model_utils):
    data = {"id": "abc123", "other_field": "test"}
    model = model_utils.to_model(data, DummyModel)
    assert isinstance(model, DummyModel)
    assert model.id == "abc123"

    with pytest.raises(PydanticBaseValidationError):
        model_utils.to_model({}, DummyModel)

    data_list = [
        {"id": "1", "other_field": "a"}, 
        {"id": "2", "other_field": "b"}
    ]
    models = model_utils.to_model_list(data_list, DummyModel)
    assert all(isinstance(m, DummyModel) for m in models)
    assert len(models) == 2

    with pytest.raises(PydanticBaseValidationError):
        model_utils.to_model_list("not a list", DummyModel)

def test_prepare_safe_update_removes_protected_fields(model_utils):
    update_data = {
        "id": "someid",
        "_id": "someid",
        "role": "admin",
        "created_at": "2023-01-01",
        "updated_at": "2023-01-02",
        "normal_field": "value",
    }
    safe_update = model_utils.prepare_safe_update(update_data)
    for protected in model_utils.config.protected_fields:
        assert protected not in safe_update
    assert safe_update.get("normal_field") == "value"

    with pytest.raises(PydanticBaseValidationError):
        model_utils.prepare_safe_update("not a dict")

def test_convert_to_response_model_and_list(model_utils):
    obj_id = ObjectId()
    data = {"_id": obj_id, "other_field": "test"}
    model = model_utils.convert_to_response_model(data, DummyModel)
    assert isinstance(model, DummyModel)
    assert model.id == str(obj_id)

    data_list = [data, data]
    models = model_utils.convert_to_response_model_list(data_list, DummyModel)
    assert all(isinstance(m, DummyModel) for m in models)
    assert len(models) == 2

def test_fetch_first_inserted_found_and_not_found(model_utils):
    obj_id = ObjectId()
    collection = DummyCollection(return_doc=True)
    model = model_utils._response_utils.fetch_first_inserted(obj_id, collection, DummyModel)
    assert model is not None
    assert model.id == str(obj_id)

    collection_no_doc = DummyCollection(return_doc=False)
    with pytest.raises(NotFoundError):
        model_utils._response_utils.fetch_first_inserted(obj_id, collection_no_doc, DummyModel)

def test_to_model_invalid_input(model_utils):
    with pytest.raises(PydanticBaseValidationError):
        model_utils.to_model(None, DummyModel)

def test_to_model_list_invalid_element_skipped(model_utils):
    data_list = [
        {"id": "valid", "other_field": "exists"}, 
        {}
    ]
    with pytest.raises(PydanticBaseValidationError):
        model_utils.to_model_list(data_list, DummyModel)

