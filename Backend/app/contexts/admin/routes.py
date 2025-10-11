from flask import Blueprint ,request 
from app.contexts.admin.data_transfer.requests import AdminCreateUserSchema, AdminUpdateUserSchema
from app.contexts.shared.decorators.wrap_response import wrap_response
from app.contexts.infra.database.db import get_db
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.admin.data_transfer.requests import (
    AdminCreateClassSchema , AdminCreateUserSchema , AdminCreateStaffSchema
)
from app.contexts.admin.data_transfer.responses import (
    AdminCreateStaffDataDTO,
    AdminUpdateUserDataDTO,
    AdminCreateUserDataDTO,
    AdminGetStaffDataDTO,
)
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from app.contexts.admin.services import AdminService
from app.contexts.staff.models import StaffMapper
from app.contexts.auth.jwt_utils import role_required

admin_bp = Blueprint('admin', __name__)




@admin_bp.route('/users', methods=['POST'])
@role_required(["admin"])
@wrap_response
def admin_create_user():
    user_schema = pydantic_converter.convert_to_model(request.json, AdminCreateUserSchema)
    admin_service = AdminService(get_db())
    admin_id = get_current_user_id() 
    user_response_dto = admin_service.admin_create_user(user_schema, created_by=admin_id)
    user_dto = AdminCreateUserDataDTO(**user_response_dto.model_dump())
    return BaseResponseDTO(data=user_dto, message="User created", success=True)

    

@admin_bp.route('/users/<user_id>', methods=['PATCH'])
@role_required(["admin"])
@wrap_response
def admin_update_user(user_id):
    user_schema = pydantic_converter.convert_to_model(request.json, AdminUpdateUserSchema)
    admin_service = AdminService(get_db())
    user_update_dto = admin_service.admin_update_user(user_id, user_schema)
    user_dto = AdminUpdateUserDataDTO(**user_update_dto.model_dump())
    return BaseResponseDTO(data=user_dto, message="User updated successfully", success=True)





@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@role_required(["admin"])
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
    payload = pydantic_converter.convert_to_model(payload, AdminCreateClassSchema)
    class_dto = AdminService(get_db()).admin_create_class(payload, created_by=admin_id)
    return BaseResponseDTO(
        data=class_dto,
        message="Class created successfully",
        success=True
    )




@admin_bp.route("/staff", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_staff():
    payload_dict = request.json
    admin_id = get_current_user_id()
    payload = pydantic_converter.convert_to_model(payload_dict, AdminCreateStaffSchema)
    user_dto, staff_dto = AdminService(get_db()).admin_create_staff(payload, admin_id)
    merged_data = {**user_dto.model_dump(), **staff_dto.model_dump()}
    merged_dto = AdminCreateStaffDataDTO(**merged_data)
    return BaseResponseDTO(
        data=merged_dto.model_dump(),
        message=f"Staff {staff_dto.staff_name} created successfully",
        success=True
    )
@admin_bp.route("/staff/<user_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_staff(user_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateUserSchema)
    admin_id = get_current_user_id()
    admin_service = AdminService(get_db())
    user_staff_dto = admin_service.admin_update_staff(user_id=user_id, payload=payload)
    return BaseResponseDTO(
        data=user_staff_dto,
        message=f"Staff {user_staff_dto.staff_name} updated successfully",
        success=True
    )


@admin_bp.route("/staff/<staff_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_staff_by_id(staff_id: str):
    admin_service = AdminService(get_db())
    staff_dto: StaffBaseDataDTO = admin_service.admin_get_staff_by_id(staff_id)
    
    return BaseResponseDTO(
        data=staff_dto,
        message="Staff retrieved",
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
    


@admin_bp.route("/student/<student_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_student_info(student_id: str):
    admin_service = AdminService(get_db())
    data = admin_service.admin_get_student_by_user_id(student_id)
    return BaseResponseDTO(
        data=data,
        message="Student retrieved",
        success=True
    )


@admin_bp.route("/student", methods=["PUT"])
@role_required(["admin"])
@wrap_response
def admin_update_student():
    payload = request.json
    admin_id = get_current_user_id()
    admin_service = AdminService(get_db())
    student_dto = admin_service.admin_update_student_info(payload, admin_id)
    
    return BaseResponseDTO(
        data=student_dto,
        message=f"Student {student_dto.student.student_id} updated successfully",
        success=True
    )
