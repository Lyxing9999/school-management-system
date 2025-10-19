from flask import Blueprint ,request 
from app.contexts.admin.data_transfer.requests import AdminCreateUserSchema, AdminUpdateUserSchema
from app.contexts.shared.decorators.wrap_response import wrap_response
from app.contexts.infra.database.db import get_db
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.admin.data_transfer.requests import (
    AdminCreateClassSchema,
    AdminCreateUserSchema,
    AdminCreateStaffSchema,
    AdminUpdateStaffSchema,
    AdminUpdateInfoStudentSchema,
    AdminUpdateClassSchema
)
from app.contexts.admin.data_transfer.responses import (
    AdminCreateStaffDataDTO,
    AdminUpdateUserDataDTO,
    AdminCreateUserDataDTO,
    PaginatedUsersDataDTO
)
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from app.contexts.admin.services import AdminService
from app.contexts.auth.jwt_utils import role_required
from app.uploads.students import save_file, delete_file
admin_bp = Blueprint('admin', __name__)

# In route
@admin_bp.route("/users", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_users_paginated():
    admin_service = AdminService(get_db())
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 5))
    roles = request.args.getlist("role[]") 
    users_list, total = admin_service.admin_get_users(roles, page=page, page_size=page_size)
    
    return PaginatedUsersDataDTO(
        users=users_list,
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
    admin_service = AdminService(get_db())
    admin_id = get_current_user_id() 
    user_response_dto = admin_service.admin_create_user(user_schema, created_by=admin_id)
    user_dto = AdminCreateUserDataDTO(**user_response_dto.model_dump())
    return user_dto
    

@admin_bp.route('/users/<user_id>', methods=['PATCH'])
@role_required(["admin"])
@wrap_response
def admin_update_user(user_id):
    user_schema = pydantic_converter.convert_to_model(request.json, AdminUpdateUserSchema)
    admin_service = AdminService(get_db())
    user_update_dto = admin_service.admin_update_user(user_id, user_schema)
    user_dto = AdminUpdateUserDataDTO(**user_update_dto.model_dump())
    return user_dto





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
    return merged_dto

@admin_bp.route("/staff/<user_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_staff(user_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateStaffSchema)
    admin_id = get_current_user_id()
    admin_service = AdminService(get_db())
    user_staff_dto = admin_service.admin_update_staff(user_id=user_id, payload=payload)
    return user_staff_dto


@admin_bp.route("/staff/<staff_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_staff_by_id(staff_id: str):
    admin_service = AdminService(get_db())
    staff_dto: StaffBaseDataDTO = admin_service.admin_get_staff_by_id(staff_id)
    return staff_dto

@admin_bp.route("/staff/academic-select", methods=["GET"])
@wrap_response
def admin_get_academic_staff_for_select():
    data = AdminService(get_db()).admin_get_academic_staff_for_select()
    return data
    



@admin_bp.route("/student/<student_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_student_info(student_id: str):
    admin_service = AdminService(get_db())
    student_dto = admin_service.admin_get_student_by_user_id(student_id)
    return student_dto


@admin_bp.route("/student/<student_id>", methods=["PATCH"])
@wrap_response
def admin_update_student(student_id: str):
    print("=== PATCH /student called ===")
    print("Form data keys:", list(request.form.keys()))
    print("Files received:", list(request.files.keys()))
    admin_service = AdminService(get_db())
    payload = dict(request.form)

    # Convert classes from JSON string to list
    if "classes" in payload:
        import json
        try:
            payload["classes"] = json.loads(payload["classes"])
        except Exception:
            payload["classes"] = []
    print("Payload after parsing classes:", payload)

    # Handle photo file
    file = request.files.get("photo_url")
    print("Received photo file:", file)
    if file:
        print(f"Received photo file: {file.filename}")
        new_photo_url = save_file(file, "students", student_id)
        payload["photo_url"] = new_photo_url
        
        # Delete old photo if replaced
        student = admin_service.admin_get_student_by_user_id(student_id)
        old_photo_url = student.photo_url if student else None
        print(f"Old photo_url: {old_photo_url} -> New: {new_photo_url}")
        if old_photo_url and old_photo_url != new_photo_url:
            delete_file(old_photo_url)
    else:
        print("No photo uploaded in this request")
    # Convert to Pydantic model
    print("Final payload before model convert:", payload)
    payload_model = pydantic_converter.convert_to_model(payload, AdminUpdateInfoStudentSchema)
    print("After convert_to_model:", payload_model)

    # Update student
    student_dto = admin_service.admin_update_student_info(student_id, payload_model)
    print("Student DTO after DB update:", student_dto)

    return student_dto





# -------------------------
# CLASS MANAGEMENT
# -------------------------

@admin_bp.route("/classes", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_class():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateClassSchema)
    admin_id = get_current_user_id()
    return AdminService(get_db()).admin_create_class(payload, created_by=admin_id)


@admin_bp.route("/classes", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_classes():
    return AdminService(get_db()).admin_get_classes()


@admin_bp.route("/classes/<class_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_class_info(class_id: str):
    return AdminService(get_db()).admin_get_class_by_id(class_id)


@admin_bp.route("/classes/<class_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_class(class_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateClassSchema)
    admin_id = get_current_user_id()
    return AdminService(get_db()).admin_update_class(class_id, payload)


@admin_bp.route("/classes/<class_id>/soft-delete", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_soft_delete_class(class_id: str):
    return AdminService(get_db()).admin_soft_delete_class(class_id)

# -------------------------
# MODIFY TEACHER
# -------------------------
@admin_bp.route("/classes/<class_id>/teacher", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def assign_teacher(class_id: str):
    teacher_id = request.json.get("teacher_id")
    return AdminService(get_db()).admin_assign_teacher(class_id, teacher_id)

@admin_bp.route("/classes/<class_id>/teacher", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def remove_teacher(class_id: str):
    teacher_id = request.json.get("teacher_id")
    # optional: teacher_id can be None for soft unassign
    return AdminService(get_db()).admin_assign_teacher(class_id, teacher_id=None)


# -------------------------
# MODIFY SUBJECTS
# --
# 
# -----------------------
@admin_bp.route("/subject", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_subjects():
    return AdminService(get_db()).admin_get_subjects()



@admin_bp.route("/subject/<subject_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_subject_info(subject_id: str):
    return AdminService(get_db()).admin_get_subject_by_id(subject_id)


@admin_bp.route("/subject", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_subject():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateSubjectSchema)
    admin_id = get_current_user_id()
    return AdminService(get_db()).admin_create_subject(payload, created_by=admin_id)

@admin_bp.route("/subject/<subject_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_subject(subject_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateSubjectSchema)
    admin_id = get_current_user_id()
    return AdminService(get_db()).admin_update_subject(subject_id, payload)

@admin_bp.route("/subject/<subject_id>", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_delete_subject(subject_id: str):
    return AdminService(get_db()).admin_delete_subject(subject_id)

# -------------------------
# MODIFY STUDENTS
# -------------------------
@admin_bp.route("/classes/<class_id>/students", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def assign_student(class_id: str):
    student_id = request.json.get("student_id")
    return AdminService(get_db()).admin_assign_student(class_id, student_id)

@admin_bp.route("/classes/<class_id>/students", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def remove_student(class_id: str):
    student_id = request.json.get("student_id")
    return AdminService(get_db()).admin_remove_student(class_id, student_id)