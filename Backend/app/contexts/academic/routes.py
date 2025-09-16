from flask import Blueprint ,request
# from app.contexts.academic_dept.services import AcademicDeptService
# from app.contexts.shared.decorators.wrap_response import wrap_response
# from app.contexts.infra.database.db import get_db
# from app.contexts.common.base_response_dto import BaseResponseDTO
# from app.contexts.academic_dept.data_transfer.requests import ClassCreateSchema
from app.contexts.shared.model_converter import converter_utils
from app.contexts.academic.data_transfer.requests import AcademicCreateUserSchema
from app.contexts.shared.decorators.wrap_response import wrap_response
from app.contexts.infra.database.db import get_db
from app.contexts.common.base_response_dto import BaseResponseDTO
from app.contexts.academic.services import AcademicService
academic_bp = Blueprint('academic', __name__)





@academic_bp.route('/classes', methods=['GET']) 
@wrap_response
def get_academic_class():
    academic_service = AcademicService(get_db())
    classes = academic_service.get_classes()
    return BaseResponseDTO(data=classes, message="Classes retrieved", success=True)

@academic_bp.route('/classes/<class_id>', methods=['PATCH'])
@wrap_response
def modify_class(class_id):
    academic_service = AcademicService(get_db())
    academic_service.modify_class(class_id)