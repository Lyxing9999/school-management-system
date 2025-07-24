from flask import Blueprint, request , jsonify, g  # type: ignore
from app.services.teacher_service import get_teacher_service
from app.auth.jwt_utils import role_required
from app.enums.roles import Role
from app.responses.response import Response 
from app.database.db import get_db # type: ignore
from app.error.exceptions import BadRequestError, ErrorSeverity, ErrorCategory
from app.utils.auth_utils import get_current_user_id
teacher_bp = Blueprint('teacher', __name__)


@teacher_bp.route('/', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_teacher_profile():
    user_id = get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    teacher_info = teacher_service.get_teacher_by_id(user_id)
    return Response.success_response(
        data=teacher_info.model_dump(),
        message="Teacher profile fetched"
    )


@teacher_bp.route('/profile', methods=['PATCH'])
@role_required([Role.TEACHER.value])
def patch_teacher_profile():
    """Update teacher profile (Teacher only)."""
    user_id = get_current_user_id()

    teacher_service = get_teacher_service(get_db())
    updated_teacher = teacher_service.patch_teacher(user_id, request.get_json())
    return Response.success_response(
        data=updated_teacher,
        message="Teacher profile updated"
    )




@teacher_bp.route('/create/classes', methods=['POST'])
@role_required([Role.TEACHER.value])
def create_teacher_class():
    """Create teacher class (Teacher only)."""
    user_id = get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.teacher_create_classes(user_id, request.get_json())
    if not result:
        raise
    return Response.success_response(
        data=result,
        message="Class created"
    )


@teacher_bp.route('/classes/<_id>', methods=['PUT'])
@role_required([Role.TEACHER.value])
def update_teacher_class(_id):
    """Update teacher class (Teacher only)."""
    user_id = get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.teacher_update_class(_id, request.get_json())
    return Response.success_response(
        data=result,
        message="Class updated"
    )




@teacher_bp.route('/classes', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_all_class():
    """Get teacher classes (Teacher only)."""
    user_id = get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.find_all_classes()
    return Response.success_response(
        data = [item.model_dump(mode="json", by_alias=True, exclude_none=True) for item in result] if result else [],
        message="Classes fetched"
    )
    
    
    
    
    
    
@teacher_bp.route('/classes/<_id>', methods=['GET'])
def get_class_by_id(_id):
    """Get teacher classes (Teacher only)."""
    if not _id:
        raise BadRequestError(message="Class ID is required", status_code=400, severity=ErrorSeverity.LOW, category=ErrorCategory.VALIDATION)
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.find_classes_by_id(_id)
    return Response.success_response(
        data=result.model_dump(mode='json'),
        message="Class fetched"
    )



@teacher_bp.route('/classes/<class_id>', methods=['PUT'])
@role_required([Role.TEACHER.value])
def update_class(class_id):
    """Update class (Teacher only)."""
    user_id = get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.teacher_update_class(class_id, request.get_json())
    return Response.success_response(
        data=result.model_dump(),
        message="Class updated"
    )



@teacher_bp.route('/feedback', methods=['GET'])
@role_required([Role.TEACHER.value])
def get_feedback():
    """Get feedback (Teacher only)."""
    get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.teacher_find_all_feedback()
    result_serialized = [item.model_dump(mode="json", by_alias=True, exclude_none=True) for item in result]
    return Response.success_response(
        data=result_serialized,
        message="Feedback fetched"
    )


@teacher_bp.route('/create/feedback', methods=['POST'])
@role_required([Role.TEACHER.value])
def create_feedback():
    """Create attendance (Teacher only)."""
    get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.teacher_create_feedback(request.get_json())
    return Response.success_response(
        data=result.model_dump(by_alias=False, exclude_none=True),
        message="Feedback created"
    ), 201

@teacher_bp.route('/update/feedback/<_id>', methods=['PUT'])
@role_required([Role.TEACHER.value])
def update(_id):
    """Create attendance (Teacher only)."""
    get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.teacher_update_feedback(_id, request.get_json())
    return Response.success_response(
        data=result.model_dump(by_alias=False, exclude_none=True),
        message="updated"
    ), 200

@teacher_bp.route('/feedback/<_id>', methods=['DELETE'])
@role_required([Role.TEACHER.value])
def delete_feedback(_id):
    """Delete feedback (Teacher only)."""
    get_current_user_id()
    teacher_service = get_teacher_service(get_db())
    result = teacher_service.teacher_delete_feedback(_id)
    return Response.success_response(
        data=result.model_dump(by_alias=True, exclude_none=True),
        message="Feedback deleted"  
    ), 200



# Admin handles teacher creation — disabling teacher self-creation for now
"""
@teacher_bp.route('/create/profile', methods=['POST'])
@role_required([Role.TEACHER.value])
def create_teacher_profile():
    data = request.get_json()
    if not data:
        raise BadRequestError(
            message="No data provided",
            user_message="Request body must be valid JSON.",
            details={"received": str(data)}
        )

    teacher_service = get_teacher_service(get_db())
    result = teacher_service.create_teacher(data)

    if not result:
        raise NotFoundError(
            message="Teacher profile not created",
            resource_type="Teacher",
            resource_id=g.user["id"]  # ✅ use g.user directly
        )

    return Response.success_response(
        data=result.model_dump(mode="json", by_alias=True, exclude_none=True),
        message="Teacher profile created"
    )
"""