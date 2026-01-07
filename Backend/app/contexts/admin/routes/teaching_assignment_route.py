from flask import request, g
from app.contexts.admin.routes import admin_bp

from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter
from app.contexts.core.security.auth_utils import get_current_staff_id

from app.contexts.admin.data_transfer.requests import (
    AdminAssignSubjectTeacherRequest,
    AdminUnassignSubjectTeacherRequest,
)
from app.contexts.admin.data_transfer.responses import (
    AdminTeachingAssignmentListDTO,
    AdminTeachingAssignmentDTO,
    AdminTeachingAssignmentWriteResultDTO,
)


@admin_bp.route("/classes/<class_id>/assignments", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_class_assignments(class_id: str):
    show_deleted = request.args.get("show_deleted") or "active"
    docs = g.admin.teaching_assignment_service.list_assignments_for_class(
        class_id=class_id,
        show_deleted=show_deleted,
    )
    items = mongo_converter.list_to_dto(docs, AdminTeachingAssignmentDTO)
    return AdminTeachingAssignmentListDTO(items=items)


@admin_bp.route("/classes/<class_id>/assignments", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_assign_subject_teacher(class_id: str):
    actor_id = get_current_staff_id()
    body = pydantic_converter.convert_to_model(request.json, AdminAssignSubjectTeacherRequest)

    result = g.admin.teaching_assignment_service.assign_subject_teacher(
        class_id=class_id,
        subject_id=body.subject_id,
        teacher_id=body.teacher_id,
        actor_id=actor_id,
        overwrite=bool(body.overwrite),
    )
    return AdminTeachingAssignmentWriteResultDTO(**result)


@admin_bp.route("/classes/<class_id>/assignments", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_unassign_subject_teacher(class_id: str):
    actor_id = get_current_staff_id()
    body = pydantic_converter.convert_to_model(request.json, AdminUnassignSubjectTeacherRequest)

    result = g.admin.teaching_assignment_service.unassign_subject_teacher(
        class_id=class_id,
        subject_id=body.subject_id,
        actor_id=actor_id,
    )
    return result