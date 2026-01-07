
from flask import request, g

from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter, mongo_converter

from app.contexts.teacher.data_transfer.requests import (
    TeacherAddGradeRequest,
    TeacherUpdateGradeScoreRequest,
    TeacherChangeGradeTypeRequest,
)
from app.contexts.teacher.data_transfer.responses import (
    TeacherGradePagedListDTO,
    TeacherGradeDTO,
)

@teacher_bp.route("/grades", methods=["POST"])
@role_required(["teacher"])
@wrap_response
def add_grade():
    teacher_id = get_current_staff_id()
    body = pydantic_converter.convert_to_model(request.json, TeacherAddGradeRequest)
    return g.teacher_service.add_grade(teacher_id, body)


@teacher_bp.route("/grades/<grade_id>/score", methods=["PATCH"])
@role_required(["teacher"])
@wrap_response
def update_grade_score(grade_id: str):
    teacher_id = get_current_staff_id()
    body = pydantic_converter.convert_to_model(request.json, TeacherUpdateGradeScoreRequest)
    return g.teacher_service.update_grade_score(teacher_id=teacher_id, grade_id=grade_id, payload=body)


@teacher_bp.route("/grades/<grade_id>/type", methods=["PATCH"])
@role_required(["teacher"])
@wrap_response
def change_grade_type(grade_id: str):
    teacher_id = get_current_staff_id()
    body = pydantic_converter.convert_to_model(request.json, TeacherChangeGradeTypeRequest)
    return g.teacher_service.change_grade_type(teacher_id=teacher_id, grade_id=grade_id, payload=body)


@teacher_bp.route("/classes/<class_id>/grades", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def list_grades_for_class_enriched(class_id: str):
    teacher_id = get_current_staff_id()

    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    term = request.args.get("term")
    grade_type = request.args.get("type")
    q = request.args.get("q")

   
    subject_id = request.args.get("subject_id")

    result = g.teacher_service.list_grades_for_class_enriched_paged(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id,
        page=page,
        page_size=page_size,
        term=term,
        grade_type=grade_type,
        q=q,
    )

    items = mongo_converter.list_to_dto(result["items"], TeacherGradeDTO)

    return TeacherGradePagedListDTO(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"],
    )



@teacher_bp.route("/grades/<grade_id>", methods=["DELETE"])
@role_required(["teacher"])
@wrap_response
def soft_delete_grade(grade_id: str):
    teacher_id = get_current_staff_id()

    modified = g.teacher_service.soft_delete_grade(
        teacher_id=teacher_id,
        grade_id=grade_id,
    )

    return {
        "deleted": bool(modified),
        "modified_count": int(modified or 0),
    }


@teacher_bp.route("/grades/<grade_id>/restore", methods=["POST"])
@role_required(["teacher"])
@wrap_response
def restore_grade(grade_id: str):
    teacher_id = get_current_staff_id()

    modified = g.teacher_service.restore_grade(
        teacher_id=teacher_id,
        grade_id=grade_id,
    )

    return {
        "restored": bool(modified),
        "modified_count": int(modified or 0),
    }