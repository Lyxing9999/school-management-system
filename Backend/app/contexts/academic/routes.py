
# from flask import Blueprint ,request
# from app.contexts.academic_dept.services import AcademicDeptService
# from app.contexts.shared.decorators.wrap_response import wrap_response
# from app.contexts.infra.database.db import get_db
# from app.contexts.common.base_response_dto import BaseResponseDTO
# from app.contexts.academic_dept.data_transfer.requests import ClassCreateSchema
# from app.contexts.shared.model_converter import pydantic_converter
# from app.contexts.shared.decorators.response_decorator import wrap_response
# from app.contexts.infra.database.db import get_db
# from app.contexts.common.base_response_dto import BaseResponseDTO
# from app.contexts.academic.services import AcademicService
# from app.contexts.academic.data_transfer.requests import(
#     AcademicCreateClassSchema, 
#     AcademicUpdateUserSchema, 
#     AcademicCreateStudentSchema, 
#     AcademicUpdateStudentInfoSchema
# )
# from app.contexts.core.security.auth_utils import get_current_user_id
# from app.contexts.academic.data_transfer.responses import (
#     AcademicUpdateUserDTO,
#     AcademicStudentsPageDTO,
#     AcademicCreateStudentDTO,
# )
# from app.uploads.students import save_file, delete_file

# academic_bp = Blueprint('academic', __name__)



# @academic_bp.route("/students", methods=["GET"])
# @wrap_response
# def academic_get_students_page():
#     academic_service = AcademicService(get_db())
#     page = int(request.args.get("page", 1))
#     page_size = int(request.args.get("pageSize", 5))
#     students_dto, total = academic_service.academic_get_students_page(page=page, page_size=page_size)
#     return AcademicStudentsPageDTO(
#         users=students_dto,
#         total=total,
#         page=page,
#         page_size=page_size,
#         total_pages=max((total + page_size - 1) // page_size, 1)
#     )


# @academic_bp.route("/student", methods=["POST"])
# @wrap_response
# def academic_create_student():
#     academic_service = AcademicService(get_db())
#     create_schema = pydantic_converter.convert_to_model(request.json, AcademicCreateStudentSchema)
#     created_by = get_current_user_id()  
#     student_dto = academic_service.academic_create_student(create_schema, created_by)
#     return student_dto

# @academic_bp.route("/student/<user_id>", methods=["PATCH"])
# @wrap_response
# def academic_update_iam_user(user_id: str):
#     academic_service = AcademicService(get_db())
#     update_schema = pydantic_converter.convert_to_model(request.json, AcademicUpdateUserSchema)
#     updated_user = academic_service.academic_update_iam_user(user_id, update_schema)
#     return updated_user
    

# @academic_bp.route("/student/<user_id>", methods=["DELETE"])
# @wrap_response
# def academic_delete_iam_user(user_id: str):
#     academic_service = AcademicService(get_db())
#     deleted_user: bool = academic_service.academic_delete_iam_user(user_id)
#     return deleted_user

# @academic_bp.route("/student-info/<student_id>", methods=["GET"])
# @wrap_response
# def academic_get_student_info(student_id: str):
#     academic_service = AcademicService(get_db())
#     student_dto = academic_service.academic_get_student_info(student_id)
#     return student_dto

# @academic_bp.route("/student-info/<student_id>", methods=["PATCH"])
# @wrap_response
# def academic_update_student_info(student_id: str):
#     print("=== PATCH /student called ===")
#     print("Form data keys:", list(request.form.keys()))
#     print("Files received:", list(request.files.keys()))
#     academic_service = AcademicService(get_db())
#     payload = dict(request.form)

#     # Convert classes from JSON string to list
#     if "classes" in payload:
#         import json
#         try:
#             payload["classes"] = json.loads(payload["classes"])
#         except Exception:
#             payload["classes"] = []
#     print("Payload after parsing classes:", payload)

#     # Handle photo file
#     file = request.files.get("photo_url")
#     print("Received photo file:", file)
#     if file:
#         print(f"Received photo file: {file.filename}")
#         new_photo_url = save_file(file, "students", student_id)
#         payload["photo_url"] = new_photo_url
        
#         # Delete old photo if replaced
#         student = academic_service.academic_get_student_info(student_id)
#         old_photo_url = student.photo_url if student else None
#         print(f"Old photo_url: {old_photo_url} -> New: {new_photo_url}")
#         if old_photo_url and old_photo_url != new_photo_url:
#             delete_file(old_photo_url)
#     else:
#         print("No photo uploaded in this request")
#     # Convert to Pydantic model
#     print("Final payload before model convert:", payload)
#     payload_model = pydantic_converter.convert_to_model(payload, AcademicUpdateStudentInfoSchema)
#     print("After convert_to_model:", payload_model)

#     # Update student
#     student_dto = academic_service.academic_update_student_info(student_id, payload_model)
#     print("Student DTO after DB update:", student_dto)

#     return student_dto










# @academic_bp.route("/classes", methods=["GET"])
# @wrap_response
# def academic_get_all_classes():
#     academic_service = AcademicService(get_db())
#     classes_dto = academic_service.academic_get_all_classes()
#     return BaseResponseDTO(
#         data=[
#             {**c.model_dump(), 
#                 "created_at": c.created_at.isoformat() if c.created_at else None,
#                 "updated_at": c.updated_at.isoformat() if c.updated_at else None,
#                 "deleted_at": c.deleted_at.isoformat() if c.deleted_at else None
#             } 
#             for c in classes_dto
#         ],
#         message="Classes retrieved",
#         success=True
#     )

# @academic_bp.route("/classes", methods=["POST"])
# @wrap_response
# def academic_create_class():
#     academic_service = AcademicService(get_db())
#     created_by = get_current_user_id()
#     data = request.json
#     class_create_schema = converter_utils.convert_to_model(data, AcademicCreateClassSchema)
#     class_dto = academic_service.academic_create_class(class_create_schema, created_by)
#     return BaseResponseDTO(
#         data = class_dto,
#         message="Class created successfully!",
#         success=True
#     )


# @academic_bp.route("/staff_name_select", methods=["GET"])
# @wrap_response
# def academic_get_staff_name_select():
#     academic_service = AcademicService(get_db())
#     search_text = request.args.get("search_text", "")
#     staff_name_select_dto = academic_service.academic_get_staff_name_select(search_text)
#     return BaseResponseDTO(
#         data=staff_name_select_dto,
#         message="Staff name select retrieved",
#         success=True
#     )


# @academic_bp.route("/teacher_names", methods=["GET"])
# @wrap_response
# def academic_get_teacher_names():
#     academic_service = AcademicService(get_db())
#     teacher_names_dto = academic_service.academic_list_teacher_names()
#     return BaseResponseDTO(
#         data=teacher_names_dto,
#         message="Teacher names retrieved",
#         success=True
#     )
