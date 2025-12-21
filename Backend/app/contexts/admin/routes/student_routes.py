from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter
from app.contexts.core.security.auth_utils import get_current_staff_id

# Import Schemas & DTOs
from app.contexts.admin.data_transfer.requests import AdminCreateStudentSchema, AdminUpdateStudentSchema
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.student.mapper.student_mapper import StudentMapper
from app.contexts.admin.data_transfer.responses import AdminCreateStudentDataDTO, AdminStudentNameSelectDTO, AdminStudentNameSelectListDTO

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



@admin_bp.route("/students/user/<user_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_student_by_user_id(user_id: str):
    student = g.admin.student_service.admin_get_student_by_user_id(user_id)
    return StudentMapper.to_dto(student)


@admin_bp.route("/students/user/<user_id>", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_update_student(user_id: str):
    schema = pydantic_converter.convert_to_model(request.json, AdminUpdateStudentSchema)
    student = g.admin.student_service.admin_update_student_profile(user_id, schema)
    return StudentMapper.to_dto(student)




@admin_bp.route('/students/student-select', methods=['GET'])
@role_required(["admin"])
@wrap_response
def admin_list_student_select():
    students = g.admin.student_service.admin_list_student_select_options()
    students = mongo_converter.list_to_dto(students, AdminStudentNameSelectDTO)
    return AdminStudentNameSelectListDTO(items=students)
