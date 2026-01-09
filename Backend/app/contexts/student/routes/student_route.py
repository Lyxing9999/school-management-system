from __future__ import annotations
from flask import request, g
from app.contexts.student.routes import student_bp
from app.contexts.core.security.auth_utils import get_current_student_id
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.student.data_transfer.requests import StudentGradesFilterSchema
from app.contexts.student.data_transfer.responses import (
    StudentClassListDTO,
    StudentAttendanceListDTO,
    StudentGradePagedDTO,
    StudentScheduleListDTO,
    StudentClassSectionDTO,
    StudentGradeDTO,
    StudentScheduleDTO,
    StudentAttendanceDTO,
    
)


@student_bp.route("/me/classes", methods=["GET"])
@role_required(["student"])
@wrap_response
def get_my_classes():
    student_id = get_current_student_id()
    classes = g.student_service.get_my_classes(student_id)
    items = mongo_converter.list_to_dto(classes, StudentClassSectionDTO)
    return StudentClassListDTO(items=items)


@student_bp.route("/me/attendance", methods=["GET"])
@role_required(["student"])
@wrap_response
def get_my_attendance():
    student_id = get_current_student_id()
    class_id = request.args.get("class_id")
    attendance = g.student_service.get_my_attendance(
        student_id=student_id,
        class_id=class_id,
    )
    items = mongo_converter.list_to_dto(attendance, StudentAttendanceDTO)
    return StudentAttendanceListDTO(items=items)






@student_bp.route("/me/grades", methods=["GET"])
@role_required(["student"])
@wrap_response
def get_my_grades():
    student_id = get_current_student_id()

    raw = request.args.to_dict(flat=True)
    if raw.get("term") == "":
        raw["term"] = None

    filters = StudentGradesFilterSchema.model_validate(raw)

    res = g.student_service.get_my_grades(
        student_id=student_id,
        page=filters.page,
        page_size=filters.page_size,
        term=filters.term,          
        grade_type=filters.grade_type,
        q=filters.q,
        class_id=filters.class_id,
        subject_id=filters.subject_id,
    )

    docs = (res or {}).get("items") or []
    items = mongo_converter.list_to_dto(docs, StudentGradeDTO)

    return StudentGradePagedDTO(
        items=items,
        total=int(res.get("total") or 0),
        page=int(res.get("page") or filters.page),
        page_size=int(res.get("page_size") or filters.page_size),
        pages=int(res.get("pages") or 1),
    )

@student_bp.route("/me/schedule", methods=["GET"])
@role_required(["student"])
@wrap_response
def get_my_schedule():
    student_id = get_current_student_id()
    schedule = g.student_service.get_my_schedule(student_id)
    items = mongo_converter.list_to_dto(schedule, StudentScheduleDTO)
    return StudentScheduleListDTO(items=items)