from flask import Blueprint ,request 
from app.contexts.admin.data_transfer.requests import AdminCreateUserSchema, AdminUpdateUserSchema
from app.contexts.shared.decorators.wrap_response import wrap_response
from app.contexts.shared.model_converter import converter_utils
from app.contexts.infra.database.db import get_db
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.admin.data_transfer.requests import AdminCreateClassSchema , AdminCreateStaffSchema
from app.contexts.admin.data_transfer.responses import AdminCreateUserDataDTO , AdminCreateClassDataDTO , AdminBaseUserDataDTO , AdminCreateStaffDataDTO , AdminBaseStaffDataDTO
from app.contexts.admin.services import AdminService
from app.contexts.auth.jwt_utils import role_required

admin_bp = Blueprint('admin', __name__)





@admin_bp.route('/users', methods=['POST'])
@role_required(["admin"])
@wrap_response
def admin_create_user():
    user_schema = converter_utils.convert_to_model(request.json, AdminCreateUserSchema)
    admin_service = AdminService(get_db())
    admin_id = get_current_user_id() 
    user_dto = admin_service.admin_create_user(user_schema, admin_id)
    user_dict = admin_service.iam_service.to_safe_dict(user_dto)
    user_dto = AdminCreateUserDataDTO(**user_dict)
    return BaseResponseDTO(data=user_dto, message="User created", success=True)


@admin_bp.route('/users/<user_id>', methods=['PATCH'])
@role_required(["admin"])
@wrap_response
def admin_update_user(user_id):
    user_schema = converter_utils.convert_to_model(request.json, AdminUpdateUserSchema)
    admin_service = AdminService(get_db())
    safe_dict = admin_service.admin_update_user(user_id, user_schema)
    user_dto = AdminBaseUserDataDTO(**safe_dict)
    return BaseResponseDTO(data=user_dto, message="User updated successfully", success=True)


@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@wrap_response
def admin_soft_delete_user(user_id):
    admin_service = AdminService(get_db())
    admin_service.admin_soft_delete_user(user_id)
    return BaseResponseDTO(
            data="User deleted successfully",
            message="User deleted successfully",
            success=True
        )



# In route
@admin_bp.route("/users", methods=["GET"])
@role_required(["admin"])
@wrap_response
def get_users():
    admin_service = AdminService(get_db())
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 5))
    roles = request.args.getlist("role[]") 
    users_list, total = admin_service.admin_get_users(roles, page=page, page_size=page_size)
    data = {
            "users": [
                {**u.model_dump(), 
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "updated_at": u.updated_at.isoformat() if u.updated_at else None,
                "deleted_at": u.deleted_at.isoformat() if u.deleted_at else None
                } 
                for u in users_list
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max((total + page_size - 1) // page_size, 1),
        }
    return BaseResponseDTO(
        data=data,
        message="Users retrieved",
        success=True,
    )





# -------------------------
# Class requests name owner_id grade 
# -------------------------



@admin_bp.route("/classes", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_class():
    payload = request.json
    admin_id = get_current_user_id()
    payload = converter_utils.convert_to_model(payload, AdminCreateClassSchema)
    class_dto = AdminService(get_db()).admin_create_class(payload, created_by=admin_id)
    dto = AdminCreateClassDataDTO(**class_dto)
    return BaseResponseDTO(
        data=dto,
        message="Class created successfully",
        success=True
    )





@admin_bp.route("/staff", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_staff():
    payload = request.json
    admin_id = get_current_user_id()
    payload = converter_utils.convert_to_model(payload, AdminCreateStaffSchema)
    user , staff = AdminService(get_db()).admin_create_staff(payload, admin_id)
    user = AdminBaseUserDataDTO(**user)
    staff = AdminBaseStaffDataDTO(**staff)
    dto = AdminCreateStaffDataDTO(user=user, staff=staff)
    return BaseResponseDTO(
        data=dto,
        message=f"Staff {dto.staff.staff_id} created successfully",
        success=True
    )








@admin_bp.route("/staff/academic-select", methods=["GET"])
@wrap_response
def admin_get_academic_staff_for_select():
    data = AdminService(get_db()).admin_get_academic_staff_for_select()
    return BaseResponseDTO(
        data=data,
        message="Staff retrieved",
        success=True
    )
    

