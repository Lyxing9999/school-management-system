from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.admin.data_transfer.requests import (
    AdminCreateUserSchema,
    AdminUpdateUserSchema,
    AdminSetUserStatusSchema
)
from app.contexts.admin.data_transfer.responses import (
    PaginatedUsersDataDTO,
    AdminSetUserStatusDTO,  
    PaginatedUserItemDTO,
)
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.iam.mapper.iam_mapper import IAMMapper 
from app.contexts.shared.model_converter import mongo_converter

@admin_bp.route("/users", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_users_paginated():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 5))
    roles = request.args.getlist("role[]") or request.args.getlist("role")
    search = request.args.get("search")

    cursor, total = g.admin.user_service.admin_get_users(
        roles, page=page, page_size=page_size, search=search
    )
    cursor = mongo_converter.list_to_dto(cursor, PaginatedUserItemDTO)

    return PaginatedUsersDataDTO(
        items=cursor,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max((total + page_size - 1) // page_size, 1)
        )
        
@admin_bp.route('/users', methods=['POST'])
@role_required(["admin"])
@wrap_response
def admin_create_user():
    user_schema = pydantic_converter.convert_to_model(request.json, AdminCreateUserSchema)
    admin_id = get_current_staff_id()
    user_response_dto = g.admin.user_service.admin_create_user(
        user_schema, created_by=admin_id
    )
    return IAMMapper.to_dto(user_response_dto)

@admin_bp.route("/users/<user_id>/password-reset", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_request_password_reset(user_id: str):
    admin_id = get_current_staff_id()
    return g.admin.user_service.admin_request_password_reset(target_user_id=user_id, admin_id=admin_id)

@admin_bp.route('/users/<user_id>', methods=['PATCH'])
@role_required(["admin"])
@wrap_response
def admin_update_user(user_id):
    user_schema = pydantic_converter.convert_to_model(request.json, AdminUpdateUserSchema)
    user_update_dto = g.admin.user_service.admin_update_user(user_id, user_schema)
    return IAMMapper.to_dto(user_update_dto)


@admin_bp.route('/users/<user_id>/status', methods=['PATCH'])
@role_required(["admin"])
@wrap_response
def admin_update_user_status(user_id):
    payload = request.get_json(silent=True) or {}
    if isinstance(payload.get("status"), dict) and isinstance(payload["status"].get("status"), str):
        payload["status"] = payload["status"]["status"]
    user_schema = pydantic_converter.convert_to_model(payload, AdminSetUserStatusSchema)
    result = g.admin.user_service.admin_set_user_status(user_id, user_schema)
    return AdminSetUserStatusDTO(status=result["status"])



@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_soft_delete_user(user_id: str):
    actor_id = get_current_staff_id()
    g.admin.user_service.admin_soft_delete_user(user_id=user_id, actor_id=actor_id)
    return BaseResponseDTO(
        data="User soft deleted successfully",
        message="User soft deleted successfully",
        success=True
    )

@admin_bp.route("/users/<user_id>/restore", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_restore_user(user_id: str):
    actor_id = get_current_staff_id()
    g.admin.user_service.admin_restore_user(user_id=user_id, actor_id=actor_id)

    return BaseResponseDTO(
        data={"id": user_id, "deleted": False},
        message="User restored successfully",
        success=True,
    )



@admin_bp.route("/users/<user_id>/hard", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_hard_delete_user(user_id: str):
    actor_id = get_current_staff_id()
    g.admin.user_service.admin_hard_delete_user(user_id=user_id, actor_id=actor_id)

    return BaseResponseDTO(
        data={"id": user_id, "hard_deleted": True},
        message="User hard deleted successfully",
        success=True,
    )
