import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock
from bson import ObjectId
from flask import Flask, g, jsonify, request

from app.contexts.admin.data_transfer.requests import AdminCreateUserSchema, AdminUpdateUserSchema
from app.contexts.admin.data_transfer.responses import AdminCreateUserDataDTO, AdminUpdateUserDataDTO
from app.contexts.shared.enum.roles import SystemRole

BASE_URL = "/api/admin/users"

@pytest.fixture
def app():
    app = Flask(__name__)

    # -----------------------------
    # Inject mock admin_facade for every request
    # -----------------------------
    @app.before_request
    def inject_admin_facade():
        mock_user_service = MagicMock()
        mock_facade = MagicMock()
        mock_facade.user_service = mock_user_service
        g.admin_facade = mock_facade

    # -----------------------------
    # Routes
    # -----------------------------
    @app.route(BASE_URL, methods=["POST"])
    def create_user():
        payload = AdminCreateUserSchema(**request.json)
        dto = g.admin_facade.user_service.admin_create_user(payload, created_by="test_admin")
        return jsonify({"success": True, "data": dto.model_dump()})

    @app.route(BASE_URL, methods=["GET"])
    def get_users():
        users_list, total = g.admin_facade.user_service.admin_get_users([], 1, 5)
        data = [u.model_dump() for u in users_list]
        return jsonify({"success": True, "data": {"total": total, "users": data}})

    @app.route(f"{BASE_URL}/<user_id>", methods=["PATCH"])
    def update_user(user_id):
        payload = AdminUpdateUserSchema(**request.json)
        dto = g.admin_facade.user_service.admin_update_user(user_id, payload)
        return jsonify({"success": True, "data": dto.model_dump()})

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_admin_create_user(client):
    payload = {"username": "Alice", "email": "alice@example.com", "password": "pass123", "role": "student"}
    mock_dto = AdminCreateUserDataDTO(
        id=str(ObjectId()),
        username="Alice",
        email="alice@example.com",
        role=SystemRole.STUDENT,
        created_by=str(ObjectId()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted=False,
        deleted_by=None
    )

    # The key: inject the mock before calling client
    g_mock = client.application.before_request_funcs[None][0]
    client.application.before_request_funcs[None][0] = lambda: setattr(g, "admin_facade", MagicMock(user_service=MagicMock(admin_create_user=lambda *a, **k: mock_dto)))

    resp = client.post(BASE_URL, json=payload)

    data = resp.get_json()
    assert resp.status_code == 200
    assert data["success"] is True
    assert data["data"]["username"] == "Alice"


def test_admin_get_users(client):
    mock_user = AdminCreateUserDataDTO(
        id=str(ObjectId()),
        username="Bob",
        email="bob@example.com",
        role=SystemRole.ADMIN,
        created_by=str(ObjectId()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted=False,
        deleted_by=None
    )

    # Inject the mock
    g_mock = client.application.before_request_funcs[None][0]
    client.application.before_request_funcs[None][0] = lambda: setattr(g, "admin_facade", MagicMock(user_service=MagicMock(admin_get_users=lambda *a, **k: ([mock_user], 1))))

    resp = client.get(BASE_URL)

    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["total"] == 1
    assert data["data"]["users"][0]["username"] == "Bob"


def test_admin_update_user(client):
    user_id = str(ObjectId())
    payload = {"username": "UpdatedName"}

    mock_dto = AdminUpdateUserDataDTO(
        id=user_id,
        username="UpdatedName",
        email="bob@example.com",
        role=SystemRole.ADMIN,
        created_by=str(ObjectId()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted=False,
        deleted_by=None
    )

    # Inject the mock
    g_mock = client.application.before_request_funcs[None][0]
    client.application.before_request_funcs[None][0] = lambda: setattr(g, "admin_facade", MagicMock(user_service=MagicMock(admin_update_user=lambda *a, **k: mock_dto)))

    resp = client.patch(f"{BASE_URL}/{user_id}", json=payload)

    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["username"] == "UpdatedName"