
# app/contexts/teacher/routes/classes_route.py
from __future__ import annotations
from flask import g

from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.teacher.data_transfer.responses import (
    TeacherClassSectionDTO,
    TeacherClassSectionListDTO,
    TeacherClassSectionSummaryDTO,
    TeacherStudentDTO,
    TeacherStudentListDTO,
)


@teacher_bp.route("/me/classes", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_my_classes_enriched():
    teacher_id = get_current_staff_id()
    classes = g.teacher_service.list_my_classes_enriched(teacher_id)
    classes_dto = mongo_converter.list_to_dto(classes, TeacherClassSectionDTO)
    return TeacherClassSectionListDTO(items=classes_dto)



@teacher_bp.route("/me/classes/summary", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_my_classes_with_summary():
    teacher_id = get_current_staff_id()
    classes, summary = g.teacher_service.list_my_classes_with_summary(teacher_id)
    classes_dto = mongo_converter.list_to_dto(classes, TeacherClassSectionDTO)
    return TeacherClassSectionSummaryDTO(items=classes_dto, summary=summary)



@teacher_bp.route("/me/classes/<class_id>/students", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_my_students_in_class(class_id: str):
    teacher_id = get_current_staff_id()
    students = g.teacher_service.list_my_students_in_class(class_id)
    students_dto = mongo_converter.list_to_dto(students, TeacherStudentDTO)
    return TeacherStudentListDTO(items=students_dto)
