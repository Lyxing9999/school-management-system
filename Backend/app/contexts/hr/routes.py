
from flask import Blueprint , request 
from flask_cors import cross_origin
from flask_cors import CORS
from app.contexts.shared.decorators.wrap_response import wrap_response
from app.contexts.shared.model_converter import converter_utils
from app.contexts.hr.data_transfer.requests import HRCreateStaffRequestSchema
from app.contexts.hr.data_transfer.responses import StaffReadDataDTO
from app.contexts.auth.jwt_utils import role_required
from app.contexts.core.security.auth_utils import get_current_user
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.hr.services import HRService
from app.contexts.infra.database.db import get_db
hr_bp = Blueprint("hr", __name__)
CORS(hr_bp, origins="http://localhost:3000", supports_credentials=True)
@hr_bp.route("/employees", methods=["POST"])
@role_required(["hr"])
@wrap_response
def create_staff():
    hr_service = HRService(get_db())

    staff_id = get_current_user(role="hr")["user_id"]
    payload = converter_utils.convert_to_model(request.json, HRCreateStaffRequestSchema)
    staff_dict = hr_service.create_employee(payload , created_by=staff_id)
    staff_dto = StaffReadDataDTO(**staff_dict)
    return BaseResponseDTO(data=staff_dto, message="Staff successfully created", success=True)



@hr_bp.route("/employees", methods=["GET"])
@wrap_response
@role_required(["hr"])
def get_employees():
    hr_service = HRService(get_db())
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    data = hr_service.get_employees(page=page, page_size=page_size)
    return BaseResponseDTO(data=data, message="Employees retrieved", success=True)
    

@hr_bp.route("/employees/details/<user_id>", methods=["GET"])
@wrap_response
@role_required(["hr"])
def get_employee_details(user_id):
    hr_service = HRService(get_db())
    staff_dto = hr_service.get_employee_details(user_id)
    return BaseResponseDTO(data=staff_dto, message="Employee details retrieved", success=True)