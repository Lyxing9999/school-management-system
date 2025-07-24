import pytest
from app.services.classes_service import ClassesService
from app.models.classes import ClassesModel
from app.utils.exceptions import ValidationError
from mongomock import MongoClient 
from bson import ObjectId

@pytest.fixture
def mock_db():
    client = MongoClient() 
    return client["test_db"]

@pytest.fixture
def service(mock_db):
    return ClassesService(mock_db)

def test_create_class_success(service):
    input_data = [
        {
            "name": "Math 101",
            "description": "Basic math class",
            "teacher_id": ObjectId("64f4cc9a8f8e4d1e9a123456"),
            "class_info": {
                "course_code": "MATH101",
                "course_title": "Mathematics I",
                "lecturer": "Dr. John Doe",
                "phone_number": "123456789",
            },
        },
        {
            "name": "Science 101",
            "description": "Intro to science",
            "teacher_id": ObjectId("64f4cc9a8f8e4d1e9a654321"),
            "class_info": {
                "course_code": "SCI101",
                "course_title": "Science I",
                "lecturer": "Dr. Jane Doe",
                "phone_number": "987654321",
            },
        },
    ]
    result = service.create_class(input_data)

    assert isinstance(result, list)
    assert len(result) == 2
    assert isinstance(result[0], ClassesModel)
    assert result[0].name == "Math 101"
    assert hasattr(result[0], "created_at")

def test_create_class_empty_input(service):
    with pytest.raises(ValidationError):
        service.create_class([])

def test_create_class_invalid_input(service):
    with pytest.raises(ValidationError):
        service.create_class("invalid")