from flask import Blueprint ,request
# from app.contexts.academic_dept.services import AcademicDeptService
# from app.contexts.shared.decorators.wrap_response import wrap_response
# from app.contexts.infra.database.db import get_db
# from app.contexts.common.base_response_dto import BaseResponseDTO
# from app.contexts.academic_dept.data_transfer.requests import ClassCreateSchema
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.shared.decorators.wrap_response import wrap_response
from app.contexts.infra.database.db import get_db
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.academic.services import AcademicService
from app.contexts.academic.data_transfer.requests import AcademicCreateClassSchema
from app.contexts.core.security.auth_utils import get_current_user_id
academic_bp = Blueprint('academic', __name__)



@academic_bp.route("/students", methods=["GET"])
@wrap_response
def academic_get_students_page():
    academic_service = AcademicService(get_db())
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 5))
    students_dto, total = academic_service.academic_get_students_page(page=page, page_size=page_size)
    
    return BaseResponseDTO(
        data={
            "students": [
                {**u.model_dump(), 
                 "created_at": u.created_at.isoformat() if u.created_at else None,
                 "updated_at": u.updated_at.isoformat() if u.updated_at else None,
                 "deleted_at": u.deleted_at.isoformat() if u.deleted_at else None
                } 
                for u in students_dto
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max((total + page_size - 1) // page_size, 1),
        },
        message="Students retrieved",
        success=True
    )


@academic_bp.route("/classes", methods=["GET"])
@wrap_response
def academic_get_all_classes():
    academic_service = AcademicService(get_db())
    classes_dto = academic_service.academic_get_all_classes()
    return BaseResponseDTO(
        data=[
            {**c.model_dump(), 
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                "deleted_at": c.deleted_at.isoformat() if c.deleted_at else None
            } 
            for c in classes_dto
        ],
        message="Classes retrieved",
        success=True
    )

@academic_bp.route("/classes", methods=["POST"])
@wrap_response
def academic_create_class():
    academic_service = AcademicService(get_db())
    created_by = get_current_user_id()
    data = request.json
    class_create_schema = converter_utils.convert_to_model(data, AcademicCreateClassSchema)
    class_dto = academic_service.academic_create_class(class_create_schema, created_by)
    return BaseResponseDTO(
        data = class_dto,
        message="Class created successfully!",
        success=True
    )


@academic_bp.route("/staff_name_select", methods=["GET"])
@wrap_response
def academic_get_staff_name_select():
    academic_service = AcademicService(get_db())
    search_text = request.args.get("search_text", "")
    staff_name_select_dto = academic_service.academic_get_staff_name_select(search_text)
    return BaseResponseDTO(
        data=staff_name_select_dto,
        message="Staff name select retrieved",
        success=True
    )


@academic_bp.route("/teacher_names", methods=["GET"])
@wrap_response
def academic_get_teacher_names():
    academic_service = AcademicService(get_db())
    teacher_names_dto = academic_service.academic_list_teacher_names()
    return BaseResponseDTO(
        data=teacher_names_dto,
        message="Teacher names retrieved",
        success=True
    )
