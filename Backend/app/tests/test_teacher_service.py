import pytest
from mongomock import MongoClient  
from app.services.teacher_service import MongoTeacherService
from app.models.user import UserModel
from app.enums.roles import Role  # if you're using Enum for roles

@pytest.fixture
def mock_db():
    client = MongoClient()
    return client["test_db"]

@pytest.fixture
def teacher_service(mock_db):
    return MongoTeacherService(mock_db)

@pytest.fixture
def input_data():
    return {
        "name": "Mr. Dara",
        "email": "dara@example.com",
        "username": "dara123",
        "password": "secret123",
        "teacher_info": {
            "subjects": ["Math", "Science"]
        }
    }

def test_create_teacher_success(teacher_service, input_data):
    result = teacher_service.create_teacher(input_data)

    # Ensure the result is not None and is a TeacherModel instance
    assert result is not None
    assert isinstance(result, UserModel)
    print(type(result))
    print(result)
    # Check values
    assert result.email == input_data["email"]
    assert result.username == input_data["username"]

    # Check role (based on enum or string)
    assert result.role == Role.TEACHER.value  # if using enum
    # or just: assert result.role == "teacher"



if __name__ == "__main__":
    pytest.main()