from __future__ import annotations
from flask import request, g

from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter

from app.contexts.teacher.data_transfer.requests import (
    TeacherMarkAttendanceRequest,
    TeacherChangeAttendanceStatusRequest,
    TeacherAddGradeRequest,
    TeacherUpdateGradeScoreRequest,
    TeacherChangeGradeTypeRequest,
)
from app.contexts.teacher.data_transfer.responses import (
    TeacherAttendanceListDTO,
    TeacherGradeListDTO,
    TeacherClassListDTO,
)


# ---------- Classes ----------

@teacher_bp.route("/me/classes", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def get_my_classes():
    teacher_id = get_current_user_id()
    classes = g.teacher_service.get_my_classes(teacher_id)
    return TeacherClassListDTO(items=classes)


# ---------- Attendance ----------

@teacher_bp.route("/attendance", methods=["POST"])
@role_required(["teacher"])
@wrap_response
def mark_attendance():
    teacher_id = get_current_user_id()
    body = pydantic_converter.convert_to_model(
        request.json,
        TeacherMarkAttendanceRequest,
    )
    record_dto = g.teacher_service.mark_attendance(teacher_id, body)
    return record_dto


@teacher_bp.route("/attendance/<attendance_id>/status", methods=["PATCH"])
@role_required(["teacher"])
@wrap_response
def change_attendance_status(attendance_id):
    teacher_id = get_current_user_id()
    body = pydantic_converter.convert_to_model(
        request.json,
        TeacherChangeAttendanceStatusRequest,
    )
    record_dto = g.teacher_service.change_attendance_status(
        teacher_id=teacher_id,
        attendance_id=attendance_id,
        payload=body,
    )
    # wrap_response + your error handler can convert None to 404
    return record_dto


@teacher_bp.route("/classes/<class_id>/attendance", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_attendance_for_class(class_id):
    teacher_id = get_current_user_id()
    items = g.teacher_service.list_attendance_for_class(
        teacher_id=teacher_id,
        class_id=class_id,
    )
    return TeacherAttendanceListDTO(items=items)


# ---------- Grades ----------

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
def update_grade_score(grade_id):
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
def change_grade_type(grade_id):
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
def list_grades_for_class(class_id):
    teacher_id = get_current_user_id()
    items = g.teacher_service.list_grades_for_class(
        teacher_id=teacher_id,
        class_id=class_id,
    )
    return TeacherGradeListDTO(items=items)