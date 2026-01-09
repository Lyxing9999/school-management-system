from flask import request, g
import math

from app.contexts.teacher.routes import teacher_bp
from app.contexts.core.security.auth_utils import get_current_staff_id
from app.contexts.iam.auth.jwt_utils import role_required
from app.contexts.shared.decorators.response_decorator import wrap_response
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.teacher.data_transfer.responses import (
    TeacherScheduleListDTO,
    TeacherScheduleDTO,
    TeacherScheduleSlotSelectListDTO,
    TeacherScheduleSlotSelectDTO,
)



@teacher_bp.route("/schedule", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def get_schedule():
    teacher_id = get_current_staff_id()

    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)

    class_id = request.args.get("class_id", type=str)
    day_of_week = request.args.get("day_of_week", type=int)
    start_time_from = request.args.get("start_time_from", type=str)
    start_time_to = request.args.get("start_time_to", type=str)

    schedules, total = g.teacher_service.list_my_schedule_enriched(
        teacher_id=teacher_id,
        page=page,
        page_size=page_size,
        sort=None,
        class_id=class_id,
        day_of_week=day_of_week,
        start_time_from=start_time_from,
        start_time_to=start_time_to,
    )

    items = mongo_converter.list_to_dto(schedules, TeacherScheduleDTO)

    pages = math.ceil((total or 0) / page_size) if page_size > 0 else 0

    return TeacherScheduleListDTO(
        items=items,
        total=int(total or 0),
        page=page,
        page_size=page_size,
        pages=pages,
    )


@teacher_bp.route("/schedule/slot-select", methods=["GET"])
@role_required(["teacher"])
@wrap_response
def get_schedule_slot_select():
    teacher_id = get_current_staff_id()

    class_id = request.args.get("class_id", type=str)
    if not class_id:
        raise ValueError("class_id is required")


    date = request.args.get("date", type=str)  # "YYYY-MM-DD"
    day_of_week = request.args.get("day_of_week", type=int)  # optional fallback
    limit = request.args.get("limit", default=200, type=int)
    
    items = g.teacher_service.list_schedule_slot_select_for_teacher(
        teacher_id=teacher_id,
        class_id=class_id,
        date=date,
        day_of_week=day_of_week,
        limit=limit,
    )

    dto_items = mongo_converter.list_to_dto(items, TeacherScheduleSlotSelectDTO)

    return TeacherScheduleSlotSelectListDTO(items=dto_items)