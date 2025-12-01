
from flask import request, g

from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter

from app.contexts.teacher.data_transfer.requests import (
    TeacherAddGradeRequest,
    TeacherUpdateGradeScoreRequest,
    TeacherChangeGradeTypeRequest,
)
from app.contexts.teacher.data_transfer.responses import (
    TeacherGradeListDTO,
)


@teacher_bp.route("/grades", methods=["POST"])
@role_required(["teacher"])
@wrap_response
def add_grade():
    teacher_id = get_current_user_id()
    body = pydantic_converter.convert_to_model(
        request.json,
        TeacherAddGradeRequest,
    )
    grade_dto = g.teacher_service.add_grade(teacher_id, body)
    return grade_dto


@teacher_bp.route("/grades/<grade_id>/score", methods=["PATCH"])
@role_required(["teacher"])
@wrap_response
def update_grade_score(grade_id: str):
    teacher_id = get_current_user_id()
    body = pydantic_converter.convert_to_model(
        request.json,
        TeacherUpdateGradeScoreRequest,
    )
    grade_dto = g.teacher_service.update_grade_score(
        teacher_id=teacher_id,
        grade_id=grade_id,
        payload=body,
    )
    return grade_dto


@teacher_bp.route("/grades/<grade_id>/type", methods=["PATCH"])
@role_required(["teacher"])
@wrap_response
def change_grade_type(grade_id: str):
    teacher_id = get_current_user_id()
    body = pydantic_converter.convert_to_model(
        request.json,
        TeacherChangeGradeTypeRequest,
    )
    grade_dto = g.teacher_service.change_grade_type(
        teacher_id=teacher_id,
        grade_id=grade_id,
        payload=body,
    )
    return grade_dto


@teacher_bp.route("/classes/<class_id>/grades", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_grades_for_class(class_id: str):
    teacher_id = get_current_user_id()
    items = g.teacher_service.list_grades_for_class(
        teacher_id=teacher_id,
        class_id=class_id,
    )
    return TeacherGradeListDTO(items=items)