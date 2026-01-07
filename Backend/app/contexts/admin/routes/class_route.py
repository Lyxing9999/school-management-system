from __future__ import annotations
from flask import request, g

from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter
import math
from app.contexts.admin.data_transfer.requests import (
    AdminCreateClassSchema,
    AdminAssignTeacherToClassSchema,
    AdminEnrollStudentToClassSchema,
    AdminUpdateClassRelationsSchema,
)

from app.contexts.school.data_transfer.responses import (
    UpdateClassRelationsRequest,
    UpdateClassRelationsResult,
)
from app.contexts.admin.mapper.school_admin_mapper import SchoolAdminMapper
from app.contexts.admin.data_transfer.responses import (
    AdminClassSelectOptionListDTO,
    AdminClassSelectOptionDTO,
    AdminClassDataDTO,
    AdminStudentNameSelectDTO,
    AdminStudentNameSelectListDTO,
    AdminStudentSelectDTO,
    AdminClassPaginatedDTO,
    PagedResultDTO,
    AdminSubjectSelectListDTO,
    AdminSubjectSelectDTO
    
)
from app.contexts.school.domain.value_objects.class_roster_update import ClassRosterUpdate


@admin_bp.route("/classes", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_create_class():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateClassSchema)
    admin_id = get_current_staff_id()

    section = g.admin.class_service.admin_create_class(payload=payload, created_by=admin_id)
    
    return SchoolAdminMapper.class_to_dto(section)


@admin_bp.route("/classes", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_classes():
    q = (request.args.get("q") or "").strip()
    page = max(int(request.args.get("page") or 1), 1)
    page_size = min(max(int(request.args.get("limit") or 10), 1), 100)

    include_deleted = (request.args.get("include_deleted") or "false").lower() == "true"
    deleted_only = (request.args.get("deleted_only") or "false").lower() == "true"

    result = g.admin.class_service.admin_list_classes_enriched(
        q=q,
        page=page,
        page_size=page_size,
        include_deleted=include_deleted,
        deleted_only=deleted_only,
    )

    items = mongo_converter.list_to_dto(result["items"], AdminClassDataDTO)
    total = int(result["total"])
    total_pages = max(1, math.ceil(total / page_size))

    return AdminClassPaginatedDTO(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

@admin_bp.route("/classes/<class_id>/teacher", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_assign_teacher_to_class(class_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminAssignTeacherToClassSchema)
    section = g.admin.class_service.admin_assign_teacher(class_id=class_id, teacher_id=payload.teacher_id)
    return SchoolAdminMapper.class_to_dto(section)


@admin_bp.route("/classes/<class_id>/teacher", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_unassign_teacher_to_class(class_id: str):
    section = g.admin.class_service.admin_unassign_teacher(class_id=class_id)
    return SchoolAdminMapper.class_to_dto(section)

@admin_bp.route("/classes/<class_id>/students", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_enroll_student_to_class(class_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminEnrollStudentToClassSchema)
    section = g.admin.class_service.admin_enroll_student(class_id=class_id, student_id=payload.student_id)
    
    return SchoolAdminMapper.class_to_dto(section)


@admin_bp.route("/classes/<class_id>/students/<student_id>", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_unenroll_student_from_class(class_id: str, student_id: str):
    section = g.admin.class_service.admin_unenroll_student(class_id=class_id, student_id=student_id)
    return SchoolAdminMapper.class_to_dto(section)


@admin_bp.route("/classes/<class_id>/soft-delete", methods=["DELETE"])
@role_required(["admin"])
@wrap_response
def admin_soft_delete_class(class_id: str):
    admin_id = get_current_staff_id()
    g.admin.class_service.admin_soft_delete_class(class_id=class_id, actor_id=admin_id)
    return {"message": "Class soft deleted"}



# ---------------------------------------------------------
# LIST Students in Class Select
# ---------------------------------------------------------
@admin_bp.route("/classes/<class_id>/students", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_students_in_class_select(class_id: str):
    students = g.admin.class_service.admin_list_students_in_class_select(class_id)
    items = mongo_converter.list_to_dto(students, AdminStudentNameSelectDTO)
    return AdminStudentNameSelectListDTO(items=items)


# ---------------------------------------------------------
# LIST Classes Select
# ---------------------------------------------------------
@admin_bp.route("/classes/names-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_classes_select():
    classes = g.admin.class_service.admin_list_classes_select()
    items = mongo_converter.list_to_dto(classes, AdminClassSelectOptionDTO)
    return AdminClassSelectOptionListDTO(items=items)



# ---------------------------------------------------------
# LIST subject-select for a CLASS
# ---------------------------------------------------------
@admin_bp.route("/classes/<class_id>/subjects/select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_class_subject_select(class_id: str):
    items = g.admin.class_service.admin_list_subjects_select_in_class(class_id)
    items_dto = mongo_converter.list_to_dto(items, AdminSubjectSelectDTO)
    return AdminSubjectSelectListDTO(items=items_dto)


@admin_bp.route("/classes/<class_id>/enrollment-student-select/search", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_search_enrollment_student_select(class_id: str):
    q = (request.args.get("q") or "").strip()
    limit = request.args.get("limit", type=int) or 20
    limit = max(1, min(limit, 50))

    if q == "":
        students = g.admin.class_service.admin_search_enrollment_student_select(class_id=class_id, q="", limit=limit)
        items = mongo_converter.list_to_dto(students, AdminStudentSelectDTO)
        return PagedResultDTO(items=items, nextCursor=None)


    if len(q) < 2:
        return PagedResultDTO(items=[], nextCursor=None)

    students = g.admin.class_service.admin_search_enrollment_student_select(class_id=class_id, q=q, limit=limit)
    items = mongo_converter.list_to_dto(students, AdminStudentSelectDTO)
    return PagedResultDTO(items=items, nextCursor=None)



@admin_bp.route("/classes/<class_id>/relations", methods=["PUT"])
@role_required(["admin"])
@wrap_response
def admin_update_class_relations(class_id: str):
    payload = pydantic_converter.convert_to_model(request.json, AdminUpdateClassRelationsSchema)

    result_dict = g.admin.class_service.admin_update_class_relations(payload=payload, class_id=class_id)
    
    dto = pydantic_converter.convert_to_model(result_dict, UpdateClassRelationsResult)
    return dto