import pytest
from unittest.mock import MagicMock
from bson import ObjectId
from app.contexts.admin.services.admin_facade_service import AdminFacadeService
from app.contexts.iam.data_transfer.responses import IAMBaseDataDTO
from app.contexts.admin.data_transfer.requests import AdminCreateUserSchema, AdminUpdateUserSchema
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.enum.roles import SystemRole
from datetime import datetime

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def user_service(mock_db):
    facade = AdminFacadeService(mock_db)
    return facade.user_service

def test_admin_create_user(user_service, monkeypatch):
    payload = AdminCreateUserSchema(
        email="test@example.com",
        password="12345678",
        username="testuser",
        role=SystemRole.STUDENT
    )
    created_by = "admin123"

    # Mock the IAM model returned by factory
    fake_model = MagicMock()
    fake_model.email = payload.email
    fake_model.username = payload.username
    fake_model.role = payload.role
    fake_model.created_by = created_by
    fake_model.created_at = datetime.utcnow()

    # Mock create_user and save_domain
    monkeypatch.setattr(user_service.iam_factory, "create_user", lambda **kwargs: fake_model)
    monkeypatch.setattr(user_service.iam_service, "save_domain", lambda model: IAMBaseDataDTO(
        id=str(ObjectId()),
        email=model.email,
        username=model.username,
        role=model.role,
        created_by=model.created_by,
        created_at=model.created_at
    ))

    dto = user_service.admin_create_user(payload, created_by)

    assert isinstance(dto, IAMBaseDataDTO)
    assert dto.email == "test@example.com"
    assert dto.role == SystemRole.STUDENT

def test_admin_update_user(user_service, monkeypatch):
    user_id = str(ObjectId())
    payload = AdminUpdateUserSchema(username="newname")

    fake_dto = IAMBaseDataDTO(
        id=user_id,
        email="update@example.com",
        username=payload.username,
        role=SystemRole.STUDENT,
        created_by="admin123",
        created_at=datetime.utcnow()
    )
    monkeypatch.setattr(user_service.iam_service, "update_info", lambda uid, pl, update_by_admin: fake_dto)

    result = user_service.admin_update_user(user_id, payload)
    assert isinstance(result, IAMBaseDataDTO)
    assert result.id == user_id
    assert result.username == "newname"

def test_admin_soft_delete_user(user_service, monkeypatch):
    user_id = ObjectId()
    fake_dto = IAMBaseDataDTO(
        id=str(user_id),
        email="deleted@example.com",
        username="softdeleted",
        role=SystemRole.STUDENT,
        deleted=True,
        deleted_at=datetime.utcnow(),
        deleted_by="admin123",
        created_by="admin123",
        created_at=datetime.utcnow()
    )
    monkeypatch.setattr(user_service.iam_service, "soft_delete", lambda uid: fake_dto)

    result = user_service.admin_soft_delete_user(user_id)
    assert isinstance(result, IAMBaseDataDTO)
    assert result.id == str(user_id)
    assert result.deleted is True
    assert result.email == "deleted@example.com"

def test_admin_hard_delete_user(user_service, monkeypatch):
    user_id = ObjectId()
    monkeypatch.setattr(user_service.iam_service, "hard_delete", lambda uid: True)

    result = user_service.admin_hard_delete_user(user_id)
    assert result is True

def test_admin_get_users(user_service, monkeypatch):
    fake_cursor = [{"_id": ObjectId(), "email": "a@example.com", "username": "userA", "role": SystemRole.STUDENT}]
    
    # Mock read model
    monkeypatch.setattr(user_service.admin_read_model, "get_page_by_role", lambda role, page, page_size: (fake_cursor, 1))
    
    # Mock mongo_converter.cursor_to_dto to return correct DTO
    def mock_cursor_to_dto(cursor, cls):
        return [
            IAMBaseDataDTO(
                id=str(doc["_id"]),
                email=doc["email"],
                username=doc["username"],
                role=doc["role"],
                created_by="admin123",
                created_at=datetime.utcnow()
            ) for doc in cursor
        ]
    monkeypatch.setattr(mongo_converter, "cursor_to_dto", mock_cursor_to_dto)

    users, total = user_service.admin_get_users([SystemRole.STUDENT], 1, 10)
    assert total == 1
    assert len(users) == 1
    assert isinstance(users[0], IAMBaseDataDTO)
    assert users[0].role == SystemRole.STUDENT