from flask import Blueprint ,request, g
from app.contexts.admin.data_transfer.requests import AdminCreateUserSchema, AdminUpdateUserSchema
from app.contexts.shared.decorators.response_decorator import wrap_response
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
    AdminUpdateClassSchema,
    AdminCreateSubjectSchema,
    AdminUpdateSubjectSchema
)
from app.contexts.admin.data_transfer.responses import (
    AdminCreateStaffDataDTO,
    AdminUpdateUserDataDTO,
    AdminCreateUserDataDTO,
    PaginatedUsersDataDTO,
    AdminStaffNameSelectDTO
)
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from app.contexts.admin.services.admin_facade_service import AdminFacadeService
from app.contexts.auth.jwt_utils import role_required
from app.uploads.students import save_file, delete_file
admin_bp = Blueprint('admin', __name__)

@admin_bp.before_app_request
def load_admin_facade():
    g.admin_facade = AdminFacadeService(get_db())


@admin_bp.route("/staff", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_staff():
    payload_dict = request.json
    admin_id = get_current_user_id()
    payload = pydantic_converter.convert_to_model(payload_dict, AdminCreateStaffSchema)
    user_dto, staff_dto = g.admin_facade.admin_create_staff(payload, admin_id)
    merged_data = {**user_dto.model_dump(), **staff_dto.model_dump()}
    merged_dto = AdminCreateStaffDataDTO(**merged_data)
    return merged_dto




@admin_bp.route("/staff/<user_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_staff(user_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateStaffSchema)
    admin_id = get_current_user_id()
    user_staff_dto = g.admin_facade.admin_update_staff(user_id=user_id, payload=payload)
    return user_staff_dto

@admin_bp.route("/staff/name-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_staff_name_select():
    search_text = request.args.get("search", "")
    role = request.args.get("role", "teacher")
    staff_name_select_dto = g.admin_facade.admin_get_staff_name_select(search_text, role)
    return staff_name_select_dto

@admin_bp.route("/staff/<staff_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_staff_by_id(staff_id: str):
    staff_dto: StaffBaseDataDTO = g.admin_facade.admin_get_staff_by_id(staff_id)
    return staff_dto



@admin_bp.route("/staff/academic-select", methods=["GET"])
@wrap_response
def admin_get_academic_staff_for_select():
    data = g.admin_facade.admin_get_academic_staff_for_select()
    return data
    



@admin_bp.route("/student/<student_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_student_info(student_id: str):
    student_dto = g.admin_facade.admin_get_student_by_user_id(student_id)
    return student_dto


@admin_bp.route("/student/<student_id>", methods=["PATCH"])
@wrap_response
def admin_update_student(student_id: str):
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
        student = g.admin_facade.admin_get_student_by_user_id(student_id)
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
    student_dto = g.admin_facade.admin_update_student_info(student_id, payload_model)
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
    return g.admin_facade.admin_create_class(payload, created_by=admin_id)


@admin_bp.route("/classes", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_classes():
    return g.admin_facade.admin_get_classes()


@admin_bp.route("/classes/<class_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_class_info(class_id: str):
    return g.admin_facade.admin_get_class_by_id(class_id)


@admin_bp.route("/classes/<class_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_class(class_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateClassSchema)
    admin_id = get_current_user_id()
    return g.admin_facade.admin_update_class(class_id, payload)


@admin_bp.route("/classes/<class_id>/soft-delete", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_soft_delete_class(class_id: str):
    return g.admin_facade.admin_soft_delete_class(class_id)

# -------------------------
# MODIFY TEACHER
# -------------------------
@admin_bp.route("/classes/<class_id>/teacher", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def assign_teacher(class_id: str):
    teacher_id = request.json.get("teacher_id")
    return g.admin_facade.admin_assign_teacher(class_id, teacher_id)

@admin_bp.route("/classes/<class_id>/teacher", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def remove_teacher(class_id: str):
    teacher_id = request.json.get("teacher_id")
    # optional: teacher_id can be None for soft unassign
    return g.admin_facade.admin_assign_teacher(class_id, teacher_id=None)


# -------------------------
# MODIFY SUBJECTS
# --
# 
# -----------------------
@admin_bp.route("/subject", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_subjects():
    subjects_dto = g.admin_facade.admin_get_subjects()
    return subjects_dto



@admin_bp.route("/subject/<subject_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_subject_info(subject_id: str):
    subject_dto = g.admin_facade.admin_get_subject_by_id(subject_id)
    return subject_dto


@admin_bp.route("/subject", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_subject():
    print("=== POST /subject called ===")
    print("request.json:", request.json)
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateSubjectSchema)
    admin_id = get_current_user_id()
    return g.admin_facade.admin_create_subject(payload, created_by=admin_id)

@admin_bp.route("/subject/<subject_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_subject(subject_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateSubjectSchema)
    admin_id = get_current_user_id()
    return g.admin_facade.admin_update_subject(subject_id, payload)

@admin_bp.route("/subject/<subject_id>", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_delete_subject(subject_id: str):
    return g.admin_facade.admin_delete_subject(subject_id)

# -------------------------
# MODIFY STUDENTS
# -------------------------
@admin_bp.route("/classes/<class_id>/students", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def assign_student(class_id: str):
    student_id = request.json.get("student_id")
    return g.admin_facade.admin_assign_student(class_id, student_id)

@admin_bp.route("/classes/<class_id>/students", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def remove_student(class_id: str):
    student_id = request.json.get("student_id")
    return g.admin_facade.admin_remove_student(class_id, student_id)
