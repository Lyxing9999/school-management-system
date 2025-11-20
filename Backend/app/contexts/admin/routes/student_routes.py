from flask import request, g
from app.contexts.admin.routes import admin_bp
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import pydantic_converter
from app.contexts.admin.data_transfer.request import AdminUpdateInfoStudentSchema
from app.uploads.students import save_file, delete_file

@admin_bp.route("/student/<student_id>", methods=["GET"])
@wrap_response
def admin_get_student_info(student_id: str):
    return g.admin_facade.admin_get_student_by_user_id(student_id)


@admin_bp.route("/student/<student_id>", methods=["PATCH"])
@wrap_response
def admin_update_student(student_id: str):
    payload = dict(request.form)
    if "classes" in payload:
        import json
        payload["classes"] = json.loads(payload["classes"])
    file = request.files.get("photo_url")
    if file:
        new_photo_url = save_file(file, "students", student_id)
        payload["photo_url"] = new_photo_url
        student = g.admin_facade.admin_get_student_by_user_id(student_id)
        old_photo_url = getattr(student, "photo_url", None)
        if old_photo_url and old_photo_url != new_photo_url:
            delete_file(old_photo_url)
    payload_model = pydantic_converter.convert_to_model(payload, AdminUpdateInfoStudentSchema)
    return g.admin_facade.admin_update_student_info(student_id, payload_model)