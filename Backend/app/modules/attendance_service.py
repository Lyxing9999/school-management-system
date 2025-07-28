from pymongo.database  import Database
from abc  import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.shared.model_utils import default_model_utils
from app.error.exceptions import AppBaseException, DatabaseError, ExceptionFactory , InternalServerError, NotFoundError, ErrorCategory, ErrorSeverity
from app.utils.objectid import ObjectId


class AttendanceServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "attendance"

class AttendanceService(ABC):
    pass



class MongoAttendanceService(AttendanceService):
    def __init__(self, config: AttendanceServiceConfig):
        self.config = config
        self.db = self.config.db
        self.collection = self.db[self.config.collection_name]
        self.utils = default_model_utils



    def find_all_attendances(self) -> List[AttendanceModel]:
        result = self.collection.find()
        try:
            if not result:
                raise DatabaseError(message="No attendances found", category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return self.utils.to_response_model_list(result)
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while getting all attendances", cause=e)


    def create_attendance(self, data: Dict[str, Any]) -> Optional[AttendanceModel]:
        try:
            attendance = self.utils._to_model(data)
            if not attendance:
                raise ExceptionFactory.validation_failed(field="data", value=data, reason="Invalid attendance data")
            result = self.collection.insert_one(attendance.model_dump(by_alias=True, exclude_none=True, mode="json"))
            return self.utils._fetch_first_inserted(result.inserted_id)
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while creating attendance", cause=e)


    def update_attendance(self, _id: ObjectId | str, data: Dict[str, Any]) -> Optional[AttendanceModel]:
        try:
            validated_id = self.utils._validate_objectid(_id)
            if not validated_id:
                raise ExceptionFactory.validation_failed(field="_id", value=_id, reason="Invalid attendance ID format")
            attendance = self.utils._to_model(data)
            result = self.collection.update_one({"_id": validated_id}, {"$set": attendance.model_dump(by_alias=True, exclude_none=True, mode="json")})
            if not result.acknowledged:
                raise DatabaseError(message="Failed to update attendance in database", details={"data": data}, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=500)
            return self.utils._fetch_first_inserted(result.inserted_id)
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while updating attendance", cause=e)

        
    def delete_attendance(self, _id: ObjectId | str) -> bool:
        validated_id = self.utils._validate_objectid(_id)
        try:
            result = self.collection.delete_one({"_id": validated_id})
            if not result.acknowledged:
                raise DatabaseError(message="Failed to delete attendance in database", details={"id": _id}, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=500)
            return True
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while deleting attendance", cause=e)


def get_attendance_service(db: Database) -> MongoAttendanceService:
    return MongoAttendanceService(AttendanceServiceConfig(db))