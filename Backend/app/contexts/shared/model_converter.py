from pydantic import ValidationError as PydanticValidationError
from typing import TypeVar, Dict, Any, Union, Type, List
from pydantic import BaseModel
import logging
from enum import Enum
from bson import ObjectId
from datetime import datetime, date

from app.contexts.core.errors.pydantic_error_exception import (
    PydanticBaseValidationError,
    AppTypeError,
)
from app.contexts.core.errors import handle_exception
from app.contexts.shared.time_utils import (
    utc_now,
    ensure_utc,
    ensure_utc_from_db,
    to_cambodia,
    coerce_date,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R", bound=BaseModel)
M = TypeVar("M", bound=BaseModel)


class Context(str, Enum):
    LIST = "list"
    DICT = "dict"
    SET = "set"
    STR = "str"
    INT = "int"
    FLOAT = "float"
    NONE = "none"
    SINGLE = "single"


class ModelConverterUtils:
    def _field_errors(self, e: PydanticValidationError) -> Dict[str, str]:
        return {
            ".".join(str(x) for x in err["loc"]) if err["loc"] else "unknown_field": err["msg"]
            for err in e.errors()
        }

    def convert_to_model(self, data: dict | BaseModel, model_class: Type[M]) -> M:
        try:
            logger.debug("Converting data to model %s: %s", model_class.__name__, data)
            if isinstance(data, BaseModel):
                data = data.model_dump()
            return model_class.model_validate(data)
        except PydanticValidationError as e:
            field_errors = self._field_errors(e)
            raise PydanticBaseValidationError(
                message=f"Validation failed for {model_class.__name__}.",
                cause=e,
                details=field_errors,
                hint=f"Ensure that the input data matches the expected schema for {model_class.__name__}.",
                user_message="One or more fields are invalid. Please review the provided data.",
            )
        except Exception as e:
            app_exc = handle_exception(e)
            logger.error("Unexpected error while converting to %s: %s", model_class.__name__, app_exc)
            raise app_exc

    def convert_to_model_list(
        self,
        data_list: list[Union[Dict[str, Any], BaseModel]],
        model_class: Type[M],
    ) -> list[M]:
        if not isinstance(data_list, list):
            raise AppTypeError(
                message="Invalid input type",
                cause=None,
                details={"expected_type": "list", "received_value": data_list},
                hint=f"Expected a list of items to convert to {model_class.__name__}",
            )

        results = []
        for data in data_list:
            try:
                model = self.convert_to_model(data, model_class)
                results.append(model)
            except Exception as e:
                app_exc = handle_exception(e)
                logger.error("Unexpected error converting list item: %s", app_exc, extra={"data": data})
                raise app_exc

        return results


class AdvancedMongoConverter:
    @staticmethod
    def convert_ids(doc: dict) -> dict:
        if not isinstance(doc, dict):
            return doc

        converted = {}
        for k, v in doc.items():
            if isinstance(v, ObjectId) or k == "_id":
                converted["id" if k == "_id" else k] = str(v)
            elif isinstance(v, dict):
                converted[k] = AdvancedMongoConverter.convert_ids(v)
            elif isinstance(v, list):
                new_list = []
                for item in v:
                    if isinstance(item, ObjectId):
                        new_list.append(str(item))
                    elif isinstance(item, dict):
                        new_list.append(AdvancedMongoConverter.convert_ids(item))
                    else:
                        new_list.append(item)
                converted[k] = new_list
            else:
                converted[k] = v

        return converted

    @classmethod
    def doc_to_dto(cls, doc: dict, dto_class: Type[BaseModel]) -> BaseModel:
        try:
            converted = cls.convert_ids(doc)
            return dto_class.model_validate(converted)
        except PydanticValidationError as e:
            field_errors = {
                ".".join(str(x) for x in err["loc"]) if err["loc"] else "unknown_field": err["msg"]
                for err in e.errors()
            }
            raise PydanticBaseValidationError(
                message=f"Validation failed for {dto_class.__name__}",
                cause=e,
                details=field_errors,
            )
        except Exception as e:
            raise handle_exception(e)

    @classmethod
    def list_to_dto(cls, docs: list[dict], dto_class: Type[BaseModel]) -> List[BaseModel]:
        if not isinstance(docs, list):
            raise AppTypeError(
                message="Expected a list of documents",
                cause=None,
                details={"received_value": docs},
                hint=f"Expected list of dicts to convert to {dto_class.__name__}",
            )

        return [cls.doc_to_dto(doc, dto_class) for doc in docs]

    @classmethod
    def cursor_to_dto(cls, cursor, dto_class: Type[BaseModel]) -> List[BaseModel]:
        try:
            docs = list(cursor)
            return cls.list_to_dto(docs, dto_class)
        except Exception as e:
            raise handle_exception(e)

    @classmethod
    def convert_to_object_id(cls, value: Union[str, ObjectId, None]) -> ObjectId | None:
        try:
            if value is None:
                return None

            if isinstance(value, ObjectId):
                return value

            if not isinstance(value, str):
                raise AppTypeError(
                    message="Expected string for ObjectId conversion",
                    cause=None,
                    details={
                        "received_type": type(value).__name__,
                        "received_value": value,
                    },
                    hint="Provide a valid Mongo ObjectId string (24 hex chars) or an ObjectId instance.",
                )

            v = value.strip()
            if not v:
                return None

            if not ObjectId.is_valid(v):
                raise AppTypeError(
                    message="Invalid ObjectId string",
                    cause=None,
                    details={"received_value": v},
                    hint="ObjectId must be a 24-character hex string (e.g., '507f1f77bcf86cd799439011').",
                )

            return ObjectId(v)

        except Exception as e:
            raise handle_exception(e)

    # -------- datetime helpers delegated to time_utils --------

    @classmethod
    def now(cls) -> datetime:
        return utc_now()

    @classmethod
    def to_mongo_datetime(cls, value: datetime | date | str | None) -> datetime | None:
        """
        Normalize app input to UTC datetime before writing to MongoDB.
        """
        try:
            return ensure_utc(value)
        except Exception as e:
            raise handle_exception(e)

    @classmethod
    def from_mongo_datetime(cls, value: datetime | None) -> datetime | None:
        """
        Normalize datetime read from MongoDB.
        Mongo naive datetime should be treated as UTC.
        """
        try:
            return ensure_utc_from_db(value)
        except Exception as e:
            raise handle_exception(e)

    @classmethod
    def to_cambodia_datetime(cls, value: datetime | date | str | None) -> datetime | None:
        try:
            return to_cambodia(value)
        except Exception as e:
            raise handle_exception(e)

    @classmethod
    def to_date(cls, value: datetime | date | str | None) -> date | None:
        try:
            return coerce_date(value)
        except Exception as e:
            raise handle_exception(e)


pydantic_converter = ModelConverterUtils()
mongo_converter = AdvancedMongoConverter

__all__ = [
    "pydantic_converter",
    "mongo_converter",
]