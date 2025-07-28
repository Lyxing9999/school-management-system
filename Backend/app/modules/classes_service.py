from app.error.exceptions import NotFoundError, DatabaseError, ExceptionFactory, InternalServerError, AppBaseException, BadRequestError, ErrorCategory, ErrorSeverity , AppTypeError
from app.shared.model_utils import default_model_utils
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any , Union
from pymongo.database import Database # type: ignore
from abc import ABC
from app.utils.convert import convert_serializable
import logging

logger = logging.getLogger(__name__)

class ClassesServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "classes"

class ClassesService(ABC):
    pass



class MongoClassesService(ClassesService):
    def __init__(self, config: ClassesServiceConfig):
        self.config = config
        self.db = config.db
        self.collection = self.db[config.collection_name]
        self.utils = default_model_utils
 

    def find_all_classes(self) -> List[ClassesModel]:
        result = self.collection.find()
        try:
            if not result:
                raise DatabaseError(message="No classes found", category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return self.utils.to_response_model_list(result)
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while getting all classes", cause=e)

    def create_classes(self, created_by: ObjectId | str, data: Dict[str, Any]) -> Optional[ClassesModel]:
        created_by_id = self.utils._validate_objectid(created_by) 
        classes = self.utils._to_model(data)                  
        classes.created_by = created_by_id

        try:
            result = self.collection.insert_one(
                classes.model_dump(by_alias=True, exclude_none=True, mode="json")
            )
            if not result.acknowledged:
                raise DatabaseError(
                    message="Failed to create classes",
                    details={"data": data},
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.DATABASE,
                    status_code=500
                )
            return self.utils._fetch_first_inserted(result.inserted_id)
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(
                message="Unexpected error creating classes",
                cause=e,
                details={"data": data}
            )
        
    def update_classes(self, _id: ObjectId | str, data: Dict[str, Any]) -> ClassesModel:
        try:
            validated_id = self.utils._validate_objectid(_id)
            data_model = self.utils._to_model(data)
            if not data_model:
                raise ExceptionFactory.validation_failed(field="data", value=data, reason="Invalid class data")

            result = self.collection.update_one(
                {"_id": validated_id},
                {"$set": data_model.model_dump(by_alias=True, exclude_none=True, mode="json")}
            )
            if result.matched_count == 0:
                raise DatabaseError(
                    message=f"Class not found with ID {_id}",
                    category=ErrorCategory.DATABASE,
                    severity=ErrorSeverity.HIGH,
                    status_code=500,
                    details={"id": _id}
                )
            
            raw_doc = self.collection.find_one({"_id": validated_id})
            convert_doc = convert_serializable(raw_doc)
            converted_doc = self.utils.to_response_model(convert_doc)
            if not converted_doc:
                raise DatabaseError(
                    message=f"Failed to convert updated class with ID {_id}",
                    category=ErrorCategory.DATABASE,
                    severity=ErrorSeverity.HIGH,
                    status_code=500,
                    details={"id": _id}
                )
            return converted_doc
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(
                message="Unexpected error occurred while updating classes",
                cause=e,
                severity=ErrorSeverity.HIGH,
                details={"id": _id}
            )
        
    
    def find_all_classes(self) -> List[ClassesModel]:
        try:
            result = self.collection.find({})
            if result:
                return self.utils.to_response_model_list(list(result))
            return []
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while finding classes", cause=e, severity=ErrorSeverity.HIGH, status_code=500)
    
    
    def find_classes_by_id(self, class_id: Union[ObjectId, str]) -> ClassesModel:
        try:
            validated_id = self.utils._validate_objectid(class_id)
            raw_doc = self.collection.find_one({"_id": validated_id})
            if not raw_doc:
                raise NotFoundError(message=f"Class not found with ID {class_id}", category=ErrorCategory.DATABASE , status_code=404, details={"id": class_id})
            return self.utils.to_response_model(raw_doc)
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while finding classes", cause=e, severity=ErrorSeverity.HIGH, details={"id": class_id}, status_code=500)



    def find_classes_by_teacher_id(self, created_by: ObjectId | str) -> List[ClassesModel]:
        try:
            validated_id = self.utils._validate_objectid(created_by)   
            result = self.collection.find({"created_by": validated_id})
            return self.utils.to_response_model_list(list(result))
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while finding classes", cause=e, details={"id": created_by})
    

    def _update_student_enrollment(self, _id: ObjectId | str, class_id: ObjectId | str, operation: str) -> Optional[ClassesModel]:
        try:
            validated_student_id = self.utils._validate_objectid(_id)
            if not validated_student_id:
                raise ExceptionFactory.validation_failed(field="_id", value=_id, reason="Invalid student ID format") 
            
            validated_class_id = self.utils._validate_objectid(class_id)
            if not validated_class_id:
                raise ExceptionFactory.validation_failed(field="class_id", value=class_id, reason="Invalid class ID format")
            
            mongo_op = {"$addToSet": {"students_enrolled": validated_student_id}} if operation == "enroll" else {"$pull": {"students_enrolled": validated_student_id}}
            
            result = self.collection.update_one({"_id": validated_class_id}, mongo_op)
            if result.matched_count == 0:
                raise NotFoundError("Class not found", details={"id": class_id})
            result = self.collection.find_one({"_id": validated_class_id})
            return self.utils.to_response_model(result) if result else None
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while updating student enrollment", cause=e, severity=ErrorSeverity.HIGH, details={"id": _id})



    def enroll_student_to_class(self, student_id: ObjectId | str, class_id: ObjectId | str) -> Optional[ClassesModel]:
        return self._update_student_enrollment(student_id, class_id, "enroll")

    def unenroll_student_from_class(self, student_id: ObjectId | str, class_id: ObjectId | str) -> Optional[ClassesModel]:
        return self._update_student_enrollment(student_id, class_id, "unenroll")



def get_classes_service(db: Database) -> MongoClassesService:
    logger.info(f"Getting classes service with collection: {ClassesModel._collection_name}")
    return MongoClassesService(ClassesServiceConfig(db))

