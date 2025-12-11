from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.core.security.auth_utils import get_current_staff_id

# Import Schemas & DTOs
from app.contexts.admin.data_transfer.request import AdminCreateStudentSchema
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.student.mapper.student_mapper import StudentMapper
from app.contexts.admin.data_transfer.response import AdminCreateStudentDataDTO

# ---------------------------------------------------------
# ADMIN STUDENT MANAGEMENT
# ---------------------------------------------------------

@admin_bp.route("/students", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_add_student():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateStudentSchema)
    admin_id = get_current_staff_id()

    result = g.admin.facade.admin_create_student_workflow(payload, created_by=admin_id)

    user_dto = IAMMapper.to_dto(result["user"])
    student_dto = StudentMapper.to_dto(result["student"])

    return AdminCreateStudentDataDTO(
        user=user_dto,
        student=student_dto
    )