from flask import request, g


from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_user_id
from app.contexts.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.teacher.data_transfer.responses import (
    TeacherScheduleListDTO,
    TeacherScheduleDTO,
)


@teacher_bp.route("/schedule", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def get_schedule():
    teacher_id = get_current_user_id()
    schedule = g.teacher_service.list_my_schedule_enriched(teacher_id)
    items = mongo_converter.list_to_dto(schedule, TeacherScheduleDTO)
    return TeacherScheduleListDTO(items=items)
