from __future__ import annotations
from flask import request, g
from app.contexts.student.routes import student_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response

from app.contexts.student.data_transfer.responses import (
    StudentClassListDTO,
    StudentAttendanceListDTO,
    StudentGradeListDTO,
    StudentScheduleListDTO,
)


@student_bp.route("/me/classes", methods=["GET"])
@role_required(["student"])
@wrap_response
def get_my_classes():
    student_id = get_current_user_id()
    classes = g.student_service.get_my_classes(student_id)
    return StudentClassListDTO(items=classes)


@student_bp.route("/me/attendance", methods=["GET"])
@role_required(["student"])
@wrap_response
def get_my_attendance():
    student_id = get_current_user_id()
    class_id = request.args.get("class_id")
    items = g.student_service.get_my_attendance(
        student_id=student_id,
        class_id=class_id,
    )
    return StudentAttendanceListDTO(items=items)





@student_bp.route("/me/grades", methods=["GET"])
@role_required(["student"])
@wrap_response
def get_my_grades():
    student_id = get_current_user_id()
    term = request.args.get("term")
    items = g.student_service.get_my_grades(
        student_id=student_id,
        term=term,
    )
    return StudentGradeListDTO(items=items)


@student_bp.route("/me/schedule", methods=["GET"])
@role_required(["student"])
@wrap_response
def get_my_schedule():
    student_id = get_current_user_id()
    items = g.student_service.get_my_schedule(student_id)
    print(items)
    return StudentScheduleListDTO(items=items)