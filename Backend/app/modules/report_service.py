
from app.error.exceptions import AppBaseException, InternalServerError, DatabaseError, ErrorCategory, ErrorSeverity
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from app.utils.objectid import ObjectId
from pymongo.database import Database
from app.shared.model_utils import default_model_utils

class ReportServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "reports"

class ReportService(ABC):
    pass


class MongoReportService(ReportService):
    def __init__(self, config: ReportServiceConfig):
        self.config = config
        self.db = config.db
        self.collection = self.db[self.config.collection_name]
        self.utils = default_model_utils



    def find_all_reports(self) -> List[ReportModel]:
        try:
            result = self.collection.find()
            if not result:
                raise DatabaseError(message="No reports found", category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return self.utils.to_response_model_list(result)
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while finding all reports", cause=e)

    def create_report(self, data: Dict[str, Any]) -> Optional[ReportModel]:
        report = self.utils._to_model(data)
        try:
            result = self.collection.insert_one(report.model_dump(by_alias=True, exclude_none=True, mode="json"))
            if not result.acknowledged:
                raise DatabaseError(message="Failed to create report in database", details={"data": data}, category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return self.utils._fetch_first_inserted(result.inserted_id)
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while creating report", cause=e)

    def update_report(self, _id: ObjectId | str, data: Dict[str, Any]) -> Optional[ReportModel]:
        validated_id = self.utils._validate_objectid(_id)
        report = self.utils._to_model(data)
        try:
            result = self.collection.update_one({"_id": validated_id}, {"$set": report.model_dump(by_alias=True, exclude_none=True, mode="json")})
            if not result.acknowledged:
                raise DatabaseError(message="Failed to update report in database", details={"data": data}, category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return self.utils.to_response_model(result)
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while updating report", cause=e)

    def delete_report(self, _id: ObjectId | str) -> bool:
        validated_id = self.utils._validate_objectid(_id)
        try:
            result = self.collection.delete_one({"_id": validated_id})
            if not result.acknowledged:
                raise DatabaseError(message="Failed to delete report in database", details={"id": _id}, category=ErrorCategory.DATABASE, status_code=500, severity=ErrorSeverity.HIGH)
            return True
        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(message="Unexpected error occurred while deleting report", cause=e)


def get_report_service(db: Database) -> MongoReportService:
    return MongoReportService(ReportServiceConfig(db))