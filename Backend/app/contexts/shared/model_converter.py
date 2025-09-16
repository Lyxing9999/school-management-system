
from pydantic import ValidationError as PydanticValidationError
from typing import TypeVar, Dict, Any , Union, Type, List
from pydantic import BaseModel
import logging
from abc import abstractmethod
from app.contexts.core.error import AppBaseException , ErrorSeverity , ErrorCategory, handle_exception 

from app.contexts.iam.error.user_exceptions import AppTypeError , PydanticBaseValidationError
from enum import Enum
from bson import ObjectId
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel) #for schema 
R = TypeVar("R", bound=BaseModel) #for dto
M = TypeVar("M", bound=BaseModel) #for model

class Context(str, Enum):
    LIST = "list"
    DICT = "dict"
    SET = "set"
    STR = "str"
    INT = "int"
    FLOAT = "float"
    NONE = "none"
    SINGLE = "single"



class ModelConverterUtils():
    def _field_errors(self, e: PydanticValidationError) -> Dict[str, str]:
        return {
            ".".join(str(x) for x in err['loc']) if err['loc'] else "unknown_field": err['msg']
            for err in e.errors()
        }

    def convert_to_model(self, data: Dict[str, Any], model_class: Type[M]) -> M | None:
        """Convert raw dict data to a Pydantic model, raising structured errors on failure."""
        try:
            logger.debug(f"Converting data to model {model_class.__name__}: {data}")
            return model_class.model_validate(data)
        except PydanticValidationError as e:
            field_errors = self._field_errors(e)
            app_exc = PydanticBaseValidationError( field_errors=field_errors, message=f"Validation failed while converting to {model_class.__name__}", cause=e)
            app_exc.hint = f"Check input data for {model_class.__name__}"
            raise app_exc
        except Exception as e:
            app_exc = handle_exception(e)
            logger.error(f"Unexpected error while converting to {model_class.__name__}: {app_exc}")
            raise app_exc

    def convert_to_model_list(self, data_list: list[Dict[str, Any]], model_class: Type[M]) -> list[M]:
        if not isinstance(data_list, list):
            raise AppTypeError(type_name="list", received_value=data_list, user_message="Invalid input type, expected a list.")
        results = []
        for data in data_list:
            try:
                model = self.convert_to_model(data, model_class)
                results.append(model)  
            except Exception as e:
                app_exc = handle_exception(e)
                logger.error(f"Unexpected error converting list item: {app_exc}", extra={"data": data})
                raise app_exc
        return results

    




class AdvancedMongoConverter:

    @staticmethod
    def convert_ids(doc: dict) -> dict:
        """Recursively convert _id and ObjectId fields to string 'id'."""
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
                        new_list.append(str(item))  # convert ObjectId to string
                    elif isinstance(item, dict):
                        new_list.append(AdvancedMongoConverter.convert_ids(item))  # recursive dict
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
            field_errors = { ".".join(str(x) for x in err['loc']) if err['loc'] else "unknown_field": err['msg'] for err in e.errors() }
            raise PydanticBaseValidationError(field_errors=field_errors, message=f"Validation failed for {dto_class.__name__}", cause=e)
        except Exception as e:
            raise handle_exception(e)

    @classmethod
    def list_to_dto(cls, docs: list[dict], dto_class: Type[BaseModel]) -> List[BaseModel]:
        if not isinstance(docs, list):
            raise AppTypeError(type_name="list", received_value=docs, user_message="Expected a list of documents.")
        results = []
        for doc in docs:
            results.append(cls.doc_to_dto(doc, dto_class))
        return results

    @classmethod
    def cursor_to_dto(cls, cursor, dto_class: Type[BaseModel]) -> List[BaseModel]:
        try:
            docs = list(cursor)
            return cls.list_to_dto(docs, dto_class)
        except Exception as e:
            raise handle_exception(e)

    @classmethod
    def convert_to_object_id(cls, value: Union[str, ObjectId]) -> ObjectId:
        try:
            if isinstance(value, ObjectId):
                return value
            if not isinstance(value, str):
                raise AppTypeError(type_name="str", received_value=value, user_message="Expected a string value.")
            return ObjectId(value)
        except Exception as e:
            raise handle_exception(e)





converter_utils = ModelConverterUtils()
mongo_converter = AdvancedMongoConverter()

__all__ = [
    "converter_utils",
    "mongo_converter"
]