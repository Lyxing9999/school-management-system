import pytest
from unittest.mock import MagicMock
from app.enums.roles import Role
from app.models.teacher import TeacherModel
from app.models.student import StudentModel
from app.models.user import UserModel
from app.services.user_service import get_user_service

def test_role_collections_mapping():
    # Arrange
    mock_db = MagicMock()
    
    # Mock the db[collection_name] calls
    mock_db.__getitem__.side_effect = lambda name: f"MOCK_COLLECTION_{name}"

    # Act
    user_service = get_user_service(mock_db)

    # Assert
    assert user_service._role_collections[Role.TEACHER.value] == "MOCK_COLLECTION_teacher"
    assert user_service._role_collections[Role.STUDENT.value] == "MOCK_COLLECTION_student"
    assert user_service._role_collections[Role.ADMIN.value] == "MOCK_COLLECTION_users"