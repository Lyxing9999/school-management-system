# from pymongo.database import Database
# from typing import Tuple , List
# from app.contexts.shared.enum.roles import UserRole
# from app.contexts.shared.model_converter import mongo_converter
# from app.contexts.academic.data_transfer.responses import (
#     AcademicFindAllClassDataDTO  , 
#     AcademicStaffNameSelectDTO, 
#     AcademicUpdateUserDTO,
#     AcademicCreateStudentDTO,
#     AcademicGetStudentInfoDataDTO
 
# )
# from app.contexts.academic.data_transfer.requests import (
#     AcademicCreateClassSchema, 
#     AcademicUpdateUserSchema, 
#     AcademicUpdateStudentInfoSchema, 
#     AcademicCreateStudentSchema
# )
# from app.contexts.shared.enum.roles import SystemRole
# from app.contexts.schools.services.class_service import ClassService
# from app.contexts.academic.read_models import academic_read_model
# from app.contexts.admin.services.admin_facade_service import AdminFacadeService
# from app.contexts.admin.data_transfer.response import IAMBaseDataDTO
# from app.contexts.iam.services.iam_service import IAMService
# from app.contexts.student.services import StudentService
# from app.contexts.core.log.log_service import LogService
# from time import time 
# class AcademicService:
#     def __init__(self, db: Database):
#         self._db = db
#         self._admin_service = None
#         self._class_service = None
#         self._academic_read_model = None
#         self._iam_service = None
#         self._student_service = None
#         self._log_service = LogService.get_instance()  

#     @property
#     def class_service(self) -> ClassService:
#         if self._class_service is None:
#             self._class_service = ClassService(self._db)
#         return self._class_service

#     @property
#     def admin_service(self) -> AdminFacadeService:
#         if self._admin_service is None:
#             self._admin_service = AdminFacadeService(self._db)
#         return self._admin_service

#     @property
#     def iam_service(self) -> IAMService:
#         if self._iam_service is None:
#             self._iam_service = IAMService(self._db)
#         return self._iam_service

#     @property
#     def academic_read_model(self) -> academic_read_model:
#         if self._academic_read_model is None:
#             self._academic_read_model = academic_read_model(self._db)
#         return self._academic_read_model
    
#     @property
#     def student_service(self) -> StudentService:
#         if self._student_service is None:
#             self._student_service = StudentService(self._db)
#         return self._student_service

#     def _log(self, operation: str, user_id: str | None = None, extra: dict | None = None, level: str = "INFO"):
#         msg = f"AcademicService::{operation}" + (f" [user_id={user_id}]" if user_id else "")  # construct message
#         self._log_service.log(msg, level=level, module="AcademicService", user_id=user_id, extra=extra or {})  # send to logger

#     # -------------------------
#     # Student Iam 
#     # -------------------------
#     def academic_get_students_page(self, page: int = 1, page_size: int = 5) -> Tuple[List[IAMBaseDataDTO], int]:
#         start = time()
#         users_dto, total = self.admin_service.admin_get_users(UserRole.STUDENT.value, page, page_size)
#         duration_ms = (time() - start) * 1000
#         self._log("academic_get_students_page", extra={"duration_ms": duration_ms})
#         return users_dto, total
#     def academic_create_student(self, create_schema: AcademicCreateStudentSchema, created_by: str) -> AcademicCreateStudentDTO:
#         start = time()
#         create_schema.role = SystemRole.STUDENT
#         user_dto = self.admin_service.admin_create_user(create_schema, created_by)
#         duration_ms = (time() - start) * 1000
#         self._log("academic_create_student", extra={"duration_ms": duration_ms})
#         return user_dto
#     def academic_update_iam_user(self, user_id: str, update_schema: AcademicUpdateUserSchema) -> AcademicUpdateUserDTO:
#         start = time()
#         update_schema.role = SystemRole.STUDENT
#         user_dto = self.iam_service.update_info(user_id, update_schema)
#         duration_ms = (time() - start) * 1000
#         self._log("academic_update_iam_user", extra={"duration_ms": duration_ms})
#         return user_dto
#     def academic_delete_iam_user(self, user_id: str) -> bool:
#         start = time()
#         deleted = self.iam_service.soft_delete(user_id)
#         duration_ms = (time() - start) * 1000
#         self._log("academic_delete_iam_user", extra={"duration_ms": duration_ms})
#         return deleted

#     # -------------------------
#     # Student info
#     # -------------------------
#     def academic_get_student_info(self, user_id: str) -> AcademicGetStudentInfoDataDTO:
#         start = time()
#         student_info = self.student_service.get_student_info(user_id)
#         duration_ms = (time() - start) * 1000
#         self._log("academic_get_student_info", extra={"duration_ms": duration_ms})
#         return student_info
#     def academic_update_student_info(self, user_id: str, update_schema: AcademicUpdateStudentInfoSchema) -> AcademicGetStudentInfoDataDTO:
#         start = time()
#         student_info = self.student_service.save_student_info(user_id, update_schema)
#         duration_ms = (time() - start) * 1000
#         self._log("academic_update_student_info", extra={"duration_ms": duration_ms})
#         return student_info
    



#     # -------------------------
#     # class routes
#     # -------------------------

#     def academic_get_all_classes(self) -> List[AcademicFindAllClassDataDTO]:
#         raw_classes = self.academic_read_model.get_all_classes()
#         return mongo_converter.cursor_to_dto(raw_classes, AcademicFindAllClassDataDTO)

#     def academic_create_class(self, class_create_schema: AcademicCreateClassSchema, created_by: str) -> dict:
#         return self.class_service.create_class(class_create_schema, created_by)
    

#     def academic_get_staff_name_select(self, search_text: str = "") -> AcademicStaffNameSelectDTO:
#         raw = self.academic_read_model.get_staff_name_select(search_text)
#         return mongo_converter.cursor_to_dto(raw, AcademicStaffNameSelectDTO)

    
#     def academic_list_teacher_names(self) -> list[dict]:
#         raw = self.academic_read_model.list_teacher_names()
#         return mongo_converter.cursor_to_dto(raw, AcademicStaffNameSelectDTO)
        