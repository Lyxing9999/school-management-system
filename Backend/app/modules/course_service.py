
from app.error.exceptions import DatabaseError, InternalServerError, AppBaseException, ErrorCategory, ErrorSeverity
from app.utils.objectid import ObjectId
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo.database import Database # type: ignore
from abc import ABC, abstractmethod
import logging
from app.shared.model_utils import default_model_utils
logger = logging.getLogger(__name__)
class CourseServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "course"


class CourseService(ABC):
    pass

class MongoCourseService(CourseService):
    def __init__(self, config: CourseServiceConfig):
        self.config = config
        self.db = config.db
        self.collection = self.db[self.config.collection_name]
        self.now = datetime.now(timezone.utc)
        self.utils = default_model_utils

    
    def get_course_by_id(self, _id: ObjectId | str) -> Optional[CourseModel]:
        validated_id = self.utils._validate_objectid(_id)
        try:
            course = self.collection.find_one({"_id": validated_id})
            if not course:
                raise DatabaseError(
                message="Course not found",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=500,
            )
            return self.utils.to_response_model(course)
        except AppBaseException as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting course by id: {e}")
            raise InternalServerError(
                message="Failed to get course by id",
                cause=e,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=500,
            )




    def create_course(self, _id: ObjectId | str, data: Dict[str, Any]) -> Optional[CourseModel]:
 
        data = self.utils._prepare_safe_update(data)
        data["created_at"] = self.now
        data["updated_at"] = self.now
        data["created_by"] = self.utils._validate_objectid(_id)
        data["updated_by"] = self.utils._validate_objectid(_id)
        data["update_history"] = self.utils._initialize_update_history()
        try:
            inserted_ids = self.collection.insert_many([data])
            return self.utils._fetch_first_inserted(inserted_ids)
        except AppBaseException as e:
            logger.error(f"Error creating course: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error creating course: {e}")
            raise InternalServerError(
                message="Failed to create course",
                cause=e,
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.DATABASE,
            )

    def update_course(self, _id: ObjectId | str, data: Dict[str, Any]) -> Optional[CourseModel]:
        validated_id = self.utils._validate_objectid(_id)
        data = self.utils._prepare_safe_update(data)
        data["updated_at"] = self.now
        data["updated_by"] = self.utils._validate_objectid(_id)
        data["update_history"] = self.utils._initialize_update_history()
        try:
            result = self.collection.update_one({"_id": validated_id}, {"$set": data})
            if not result.acknowledged:
                raise DatabaseError(
                message="Failed to update course",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=500,
                )
            return self.utils.to_response_model(result)
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(
                message="Failed to update course",
                cause=e,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=500,
            )
    
    def delete_course(self, _id: ObjectId | str) -> bool:
        validated_id = self.utils._validate_objectid(_id)
        try:
            result = self.collection.delete_one({"_id": validated_id})
            if not result.acknowledged:
                raise DatabaseError(
                message="Failed to delete course",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=500,
            )
            return True
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(
                message="Failed to delete course",
                cause=e,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=500,
            )

    def find_all_courses(self) -> List[CourseModel]:
        try:
            result = self.collection.find()
            if not result:
                raise DatabaseError(message="No courses found", category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return self.utils.to_response_model_list(result)
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while getting all courses", cause=e)

    def find_courses_by_teacher_id(self, teacher_id: ObjectId | str) -> List[CourseModel]:
        validated_id = self.utils._validate_objectid(teacher_id)
        result = self.collection.find({"teacher_id": validated_id})
        return self.utils.to_response_model_list(result)

        
        



def get_course_service(db: Database) -> MongoCourseService:
    return MongoCourseService(CourseServiceConfig(db))