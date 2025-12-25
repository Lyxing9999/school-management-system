from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter
from app.contexts.admin.data_transfer.requests import AdminCreateSubjectSchema
from app.contexts.admin.data_transfer.responses import  AdminSubjectNameSelectListDTO, AdminSubjectNameSelectDTO
from app.contexts.admin.mapper.school_admin_mapper import SchoolAdminMapper


@admin_bp.route("/subjects", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_subject():
    subject_list = g.admin.subject_service.admin_list_subject()
    return SchoolAdminMapper.subject_list_to_dto(subject_list)
    

@admin_bp.route("/subjects/<subject_id>", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_get_subject(subject_id: str):
    subject_dict: dict = g.admin.subject_service.admin_get_subject(subject_id)
    return SchoolAdminMapper.subject_doc_to_dto(subject_dict)


@admin_bp.route("/subjects", methods=["POST"])
@role_required(["admin"])
@wrap_response
def admin_create_subject():
    payload = pydantic_converter.convert_to_model(request.json, AdminCreateSubjectSchema)
    admin_id = get_current_user_id()  
    subject = g.admin.subject_service.admin_create_subject(
        payload=payload, 
        created_by=admin_id
    )
    return SchoolAdminMapper.subject_to_dto(subject)


@admin_bp.route("/subjects/<subject_id>/deactivate", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_deactivate_subject(subject_id: str):
    subject = g.admin.subject_service.admin_deactivate_subject(subject_id)
    return SchoolAdminMapper.subject_to_dto(subject)


@admin_bp.route("/subjects/<subject_id>/activate", methods=["PATCH"])
@role_required(["admin"])
@wrap_response
def admin_activate_subject(subject_id: str):
    subject = g.admin.subject_service.admin_activate_subject(subject_id)
    return SchoolAdminMapper.subject_to_dto(subject)



@admin_bp.route("/subjects/names-select", methods=["GET"])
@role_required(["admin"])
@wrap_response
def admin_list_subject_name_select():
    subject_list = g.admin.subject_service.admin_list_subject_name_select()
    subject_dto = mongo_converter.list_to_dto(subject_list, AdminSubjectNameSelectDTO)
    return AdminSubjectNameSelectListDTO(items=subject_dto)
