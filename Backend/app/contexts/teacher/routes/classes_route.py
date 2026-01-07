# app/contexts/teacher/routes/classes_route.py
from __future__ import annotations

from flask import g

from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.teacher.data_transfer.responses import (
    TeacherClassSectionDTO,
    TeacherClassSectionListDTO,
    TeacherClassSectionSummaryDTO,
    TeacherClassSummaryDTO,
    TeacherStudentDTO,
    TeacherStudentListDTO,
)


@teacher_bp.route("/me/classes", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_my_classes_enriched():
    teacher_id = get_current_staff_id()

    # This should already return enriched docs:
    # - homeroom_teacher_name
    # - subject_labels
    # - enrolled_count, subject_count, etc.
    docs = g.teacher_service.list_my_classes_enriched(teacher_id)

    items_dto = mongo_converter.list_to_dto(docs, TeacherClassSectionDTO)
    return TeacherClassSectionListDTO(items=items_dto)


@teacher_bp.route("/me/classes/summary", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_my_classes_with_summary():
    teacher_id = get_current_staff_id()

    docs, summary = g.teacher_service.list_my_classes_with_summary(teacher_id)

    items_dto = mongo_converter.list_to_dto(docs, TeacherClassSectionDTO)

    # ✅ Validate summary shape so it cannot drift silently
    summary_dto = TeacherClassSummaryDTO(**(summary or {}))

    return TeacherClassSectionSummaryDTO(items=items_dto, summary=summary_dto)


@teacher_bp.route("/me/classes/<class_id>/students", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_my_students_in_class(class_id: str):
    teacher_id = get_current_staff_id()

    # ✅ IMPORTANT: enforce permission (homeroom teacher at minimum)
    docs = g.teacher_service.list_my_students_in_class(
        teacher_id=teacher_id,
        class_id=class_id,
    )

    items_dto = mongo_converter.list_to_dto(docs, TeacherStudentDTO)
    return TeacherStudentListDTO(items=items_dto)