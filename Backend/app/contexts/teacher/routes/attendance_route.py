# app/contexts/teacher/routes/attendance_route.py
from __future__ import annotations
from flask import request, g

from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter

from app.contexts.teacher.data_transfer.requests import (
    TeacherMarkAttendanceRequest,
    TeacherChangeAttendanceStatusRequest,
)
from app.contexts.teacher.data_transfer.responses import (
    TeacherAttendanceListDTO,
    TeacherAttendanceDTO,
)


@teacher_bp.route("/attendance", methods=["POST"])
@role_required(["teacher"])
@wrap_response
def mark_attendance():
    teacher_id = get_current_staff_id()
    body = pydantic_converter.convert_to_model(
        request.json,
        TeacherMarkAttendanceRequest,
    )
    record_dto = g.teacher_service.mark_attendance(teacher_id, body)
    return record_dto


@teacher_bp.route("/attendance/<attendance_id>/status", methods=["PATCH"])
@role_required(["teacher"])
@wrap_response
def change_attendance_status(attendance_id: str):
    teacher_id = get_current_staff_id()
    body = pydantic_converter.convert_to_model(
        request.json,
        TeacherChangeAttendanceStatusRequest,
    )
    record_dto = g.teacher_service.change_attendance_status(
        teacher_id=teacher_id,
        attendance_id=attendance_id,
        payload=body,
    )
    return record_dto


@teacher_bp.route("/classes/<class_id>/attendance", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_attendance_for_class_enriched(class_id: str):

    teacher_id = get_current_staff_id()
    docs = g.teacher_service.list_attendance_for_class_enriched(
        teacher_id=teacher_id,
        class_id=class_id,
    )

    items = mongo_converter.list_to_dto(docs, TeacherAttendanceDTO)
    return TeacherAttendanceListDTO(items=items)