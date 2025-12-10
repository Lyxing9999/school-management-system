# app/contexts/teacher/routes/selects_route.py
from __future__ import annotations
from flask import g

from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.teacher.data_transfer.responses import (
    TeacherStudentNameSelectDTO,
    TeacherStudentSelectNameListDTO,
    TeacherSubjectNameSelectDTO,
    TeacherSubjectSelectNameListDTO,
    TeacherClassNameSelectDTO,
    TeacherClassNameSelectListDTO,
)


@teacher_bp.route("/classes/name-select", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_class_name_options_for_teacher():
    teacher_id = get_current_staff_id()
    classes = g.teacher_service.list_class_name_options_for_teacher(
        teacher_id=teacher_id
    )
    items = mongo_converter.list_to_dto(classes, TeacherClassNameSelectDTO)
    return TeacherClassNameSelectListDTO(items=items)


@teacher_bp.route("/me/classes/<class_id>/students", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_student_names_in_class(class_id: str):
    teacher_id = get_current_staff_id()
    students = g.teacher_service.list_student_name_options_in_class(
        class_id=class_id,
        teacher_id=teacher_id,
    )
    items = mongo_converter.list_to_dto(students, TeacherStudentNameSelectDTO)
    return TeacherStudentSelectNameListDTO(items=items)


@teacher_bp.route("/me/classes/<class_id>/subjects", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_subject_names_in_class(class_id: str):
    teacher_id = get_current_staff_id()
    subjects = g.teacher_service.list_subject_name_options_in_class(
        class_id=class_id,
        teacher_id=teacher_id,
    )
    items = mongo_converter.list_to_dto(subjects, TeacherSubjectNameSelectDTO)
    return TeacherSubjectSelectNameListDTO(items=items)