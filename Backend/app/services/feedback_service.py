from app.models.feedback import FeedbackModel
from app.error.exceptions import NotFoundError, DatabaseError, ExceptionFactory, InternalServerError, AppBaseException, BadRequestError, ErrorCategory, ErrorSeverity , AppDuplicateKeyError
from app.utils.objectid import ObjectId # type: ignore
from typing import Optional, List, Dict, Any, Union
from pymongo.database import Database # type: ignore
from abc import ABC
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError 
import logging
from app.services.base.base_utils_service import BaseServiceUtils
logger = logging.getLogger(__name__)

class FeedbackServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "feedback"

class FeedbackService(ABC):
    pass

class MongoFeedbackService(FeedbackService):
    def __init__(self, config: FeedbackServiceConfig):
        self.config = config
        self.db = config.db
        self.collection = self.db[self.config.collection_name]
        self.utils = BaseServiceUtils(self.db, FeedbackModel)




    def get_feedback_by_id(self, _id: ObjectId | str) -> Optional[FeedbackModel]:
        validated_id = self.utils._validate_objectid(_id)
        result = self.collection.find_one({"_id": validated_id})
        try:
            if not result:
                raise DatabaseError(message="Feedback not found", category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return self.utils.to_response_model(result)
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while getting feedback", cause=e, details={"id": _id})

    def get_feedback_by_student_id(self, student_id: ObjectId | str) -> Optional[FeedbackModel]:
        validated_id = self.utils._validate_objectid(student_id)
        result = self.collection.find_one({"student_id": validated_id})
        if not result:
            raise DatabaseError(message="Feedback not found", category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
        return self.utils.to_response_model(result)
        


    def find_all_feedback(self) -> List[FeedbackModel]:
        result = self.collection.find()
        try:
            if not result:
                raise DatabaseError(message="No feedback found", category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return self.utils.to_response_model_list(list(result))
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while getting all feedback", cause=e)


    def create_feedback(self,  data: Dict[str, Any]) -> Optional[FeedbackModel]:
        feedback = self.utils._to_model(data)
        prepared_data = feedback.model_dump(by_alias=True, exclude_none=True, exclude={"id", "created_at", "_id", "updated_at"})
        prepared_data['created_at'] = self.utils.get_now()
        try:
            result = self.collection.insert_one(prepared_data)
            if not result.inserted_id:
                raise DatabaseError(message="Failed to create feedback in database", details={"data": data}, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=500)

            logger.info(f"Inserted feedback ID: {result.inserted_id}")
            fetched = self.utils._fetch_first_inserted(result.inserted_id, self.collection)
            logger.info(f"Fetched inserted feedback: {fetched} (type: {type(fetched)})")
            return fetched
        except DuplicateKeyError as e:
            raise AppDuplicateKeyError(
                message="Feedback already exists for this _id or unique field.",
                details={"pymongo": str(e)}
            )
        except Exception as e:
            logger.error("Failed to fetch or return inserted feedback", exc_info=True)
            raise InternalServerError(
                message="Unexpected error occurred while fetching inserted feedback",
                cause=e,
                details={"inserted_id": str(result.inserted_id)},
            )



    def update_feedback(self, _id: ObjectId | str, data: Dict[str, Any]) -> Optional[FeedbackModel]:
        validated_id = self.utils._validate_objectid(_id)
        feedback = self.utils._to_model(data)
        prepared_data = feedback.model_dump(by_alias=True, exclude_none=True, exclude={"id", "created_at", "_id", "updated_at"})
        prepared_data['updated_at'] = self.utils.get_now()
        try:
            result = self.collection.update_one(
                {"_id": validated_id},
                {"$set": prepared_data}
            )
            if not result.acknowledged:
                raise DatabaseError(
                    message="Failed to update feedback in database",
                    details={"data": data},
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.DATABASE,
                    status_code=500
                )
            return self.utils._fetch_first_inserted(validated_id, self.collection)
        except DuplicateKeyError as e:
            raise AppDuplicateKeyError(
                message="Feedback already exists for this _id or unique field.",
                details={"pymongo": str(e)}
            )
        except AppBaseException as e:
            raise e
        except Exception as e:
            logger.critical(f"Critical error updating feedback: {e}", exc_info=True)
            raise InternalServerError(
                message="Unexpected error occurred while updating feedback",
                cause=e,
                details={"data": data},
            )

    def delete_feedback(self, _id: ObjectId | str) -> bool:
        validated_id = self.utils._validate_objectid(_id)
        try:    
            result = self.collection.delete_one({"_id": validated_id})
            if not result.acknowledged:
                raise DatabaseError(message="Failed to delete feedback in database", details={"id": _id}, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE, status_code=500)
            return True
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while deleting feedback", cause=e, details={"id": _id})






def get_feedback_service(db: Database) -> MongoFeedbackService:
    return MongoFeedbackService(FeedbackServiceConfig(db))
