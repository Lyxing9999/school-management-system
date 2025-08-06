import logging
from typing import Optional, List, Dict, Any, Union
from pymongo.database import Database 
from app.utils.objectid import ObjectId 
from abc import ABC
from app.error.exceptions import AppBaseException,ExceptionFactory, PydanticValidationError, InternalServerError, NotFoundError, DatabaseError, ErrorCategory, ErrorSeverity
logger = logging.getLogger(__name__)
from pymongo import ReturnDocument 
from app.enum.enums import Role
from app.shared.model_utils import default_model_utils
from app.dtos.classes_response_dto import ClassResponseDTO
from app.dtos.feedback_response_dto import FeedbackResponseDTO
from app.dtos.course_response_dto import CourseResponseDTO
from app.dtos.report_response_dto import ReportResponseDTO
from app.dtos.attendance_response_dto import AttendanceResponseDTO
from app.dtos.student_response_dto import StudentResponseDTO
from app.dtos.teacher.teacher_response_dto import TeacherResponseDTO
from app.dtos.users import UserResponseDTO
class TeacherServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "teacher"


class TeacherService(ABC):
    pass



class MongoTeacherService(TeacherService):
    def __init__(self, config: TeacherServiceConfig):
        self.config = config
        self.db = self.config.db 
        self.collection = self.db[self.config.collection_name]
        self.utils = default_model_utils
        self._classes_service = None
        self._user_service = None
        self._feedback_service = None
        self._course_service = None
        self._grade_service = None
        self._report_service = None
        self._attendance_service = None
        self._student_service = None

    @property
    def classes_service(self):
        if self._classes_service is None:
            from app.services.classes_service import get_classes_service
            self._classes_service = get_classes_service(self.db)
        return self._classes_service
    
    @property
    def user_service(self):
        if self._user_service is None:
            from app.services.user_service import get_user_service
            self._user_service = get_user_service(self.db)
        return self._user_service
    
    @property
    def feedback_service(self):
        if self._feedback_service is None:
            from app.services.feedback_service import get_feedback_service
            self._feedback_service = get_feedback_service(self.db)
        return self._feedback_service

    @property
    def course_service(self):
        if self._course_service is None:
            from app.services.course_service import get_course_service
            self._course_service = get_course_service(self.db)
        return self._course_service
    
    @property
    def grade_service(self):
        if self._grade_service is None:
            from app.services.grade_service import get_grade_service
            self._grade_service = get_grade_service(self.db)
        return self._grade_service
    
    @property
    def report_service(self):
        if self._report_service is None:
            from app.services.report_service import get_report_service
            self._report_service = get_report_service(self.db)
        return self._report_service
    
    @property
    def attendance_service(self):
        if self._attendance_service is None:
            from app.services.attendance_service import get_attendance_service
            self._attendance_service = get_attendance_service(self.db)
        return self._attendance_service
    
    @property
    def student_service(self):
        if self._student_service is None:
            from app.services.student_service import get_student_service
            self._student_service = get_student_service(self.db)
        return self._student_service





    def _check_dict(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict) or not data:
            raise PydanticValidationError(
                message="Data must be a non-empty dictionary",
                details=data,
                user_message="Invalid input data"
            )

    def create_teacher(self, data: dict) -> Optional[UserResponseDTO]:
        self._check_dict(data)
        data["role"] = Role.TEACHER.value
        user_model = self.user_service.create_user(data)
        return user_model

    def get_teacher_by_id(self, _id: Union[str, ObjectId]) -> TeacherResponseDTO:
        validated_id = self.utils._validate_objectid(_id)
        try:
            result = self.collection.find_one({"_id": validated_id})
            if not result: 
                raise DatabaseError(message=f"Teacher not found with ID {_id}", category=ErrorCategory.DATABASE, status_code=404, severity=ErrorSeverity.HIGH)
            return self.utils.to_response_model(result)           
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(
                message="Unexpected error occurred while fetching teacher",
                cause=e
        )


    def patch_teacher(self, _id: ObjectId, update_data: Dict[str, Any]) -> Optional[TeacherResponseDTO]:

        validated_id = self.utils._validate_objectid(_id)
        safe_update = self.utils._prepare_safe_update(update_data)
        if "teacher_info" in safe_update and isinstance(safe_update["teacher_info"], dict):
            teacher_info_updates = safe_update.pop("teacher_info")
            for key, value in teacher_info_updates.items():
                safe_update[f"teacher_info.{key}"] = value
        try:
            if not safe_update:
                raise ExceptionFactory.validation_failed(field="update_data", value=update_data, reason="No valid update data provided")

            result = self.utils.update_one(
                {"_id": validated_id},
                {"$set": safe_update},
                return_document=ReturnDocument.AFTER
            )
            return self.utils.to_response_model(result)

        except AppBaseException:
            raise 
        except Exception as e:
            raise InternalServerError(
                message="Unexpected error occurred while updating teacher",
                cause=e
            )


    def delete_teacher(self, _id: Union[ObjectId, str]) -> bool:
        validated_id = self.utils._validate_objectid(_id)
        try:
            result = self.collection.delete_one({"_id": validated_id})
            return result.deleted_count > 0 if result else False
        
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(
                message="Unexpected error occurred while deleting teacher",
                cause=e
            )

    def find_classes_by_id(self, _id: Union[ObjectId, str]) -> ClassResponseDTO:
        return self.classes_service.find_classes_by_id(_id)
    


    # classes CRUD service
    def find_classes_by_teacher_id(self, _id: Union[ObjectId, str]) -> List[ClassResponseDTO]:
        logger.info('receive from find_classes_by_teacher_id', id=str(_id))
        return self.classes_service.find_classes_by_teacher_id(_id)
    def teacher_find_all_classes(self) -> List[ClassResponseDTO]:
        logger.info('receive from teacher_find_all_classes')
        return self.classes_service.find_all_classes()
    def teacher_create_classes(self, _id: Union[ObjectId, str], class_data: Dict[str, Any]) ->  Optional[ClassResponseDTO]:
        return self.classes_service.create_classes(_id, class_data)
    def teacher_update_class(self, _id: Union[ObjectId, str], class_data: Dict[str, Any]) ->  ClassResponseDTO:
        logger.info('receive from teacher_update_class', _id=str(_id))
        return self.classes_service.update_classes(_id, class_data)




    # feedback CRUD service
    def teacher_find_all_feedback(self) -> List[FeedbackResponseDTO]:
        return self.feedback_service.find_all_feedback()
    def teacher_create_feedback(self,feedback_data: Dict[str, Any]) -> Optional[FeedbackResponseDTO]:
        logger.info('receive from teacher_create_feedback')
        return self.feedback_service.create_feedback(feedback_data)
    def teacher_update_feedback(self, _id: Union[ObjectId, str], feedback_data: Dict[str, Any]) -> Optional[FeedbackResponseDTO]:
        return self.feedback_service.update_feedback(_id, feedback_data)  
    def teacher_delete_feedback(self, _id: Union[ObjectId, str]) -> bool:
        return self.feedback_service.delete_feedback(_id)


    # course CRUD service
    def teacher_find_all_courses(self) -> List[CourseResponseDTO]:
        logger.info('receive from teacher_find_all_courses')
        return self.course_service.find_all_courses()
    def teacher_create_course(self, course_data: Dict[str, Any]) -> Optional[CourseResponseDTO]:
        logger.info('receive from teacher_create_course')
        return self.course_service.create_course(course_data)
    def teacher_update_course(self, _id: Union[ObjectId, str], course_data: Dict[str, Any]) -> Optional[CourseResponseDTO]:
        logger.info('receive from teacher_update_course', _id=str(_id))
        return self.course_service.update_course(_id, course_data)
    def teacher_delete_course(self, _id: Union[ObjectId, str]) -> bool:
        logger.info('receive from teacher_delete_course', id=str(_id))
        return self.course_service.delete_course(_id)
    



    # attendance CRUD service
    def teacher_find_all_attendances(self) -> List[AttendanceResponseDTO]:
        logger.info('receive from teacher_find_all_attendances')
        return self.attendance_service.find_all_attendances()
    def teacher_create_attendance(self, attendance_data: Dict[str, Any]) -> Optional[AttendanceResponseDTO]:
        logger.info('receive from teacher_create_attendance', attendance_data)
        return self.attendance_service.create_attendance(attendance_data)
    def teacher_update_attendance(self, _id: Union[ObjectId, str], attendance_data: Dict[str, Any]) -> Optional[AttendanceResponseDTO]:
        logger.info('receive from teacher_update_attendance', _id=str(_id))
        return self.attendance_service.update_attendance(_id, attendance_data)
    def teacher_delete_attendance(self, _id: Union[ObjectId, str]) -> bool:
        logger.info('receive from teacher_delete_attendance', _id=str(_id))
        return self.attendance_service.delete_attendance(_id)




def get_teacher_service(db: Database) -> MongoTeacherService:
    return MongoTeacherService(TeacherServiceConfig(db))





