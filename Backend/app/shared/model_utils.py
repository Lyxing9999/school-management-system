from dataclasses import field
import traceback
from app.error.exceptions import AppTypeError, PydanticBaseValidationError , InternalServerError, BadRequestError, NotFoundError, ErrorSeverity, ErrorCategory,  AppBaseException , PydanticValidationError , handle_exception
from typing import Optional, List, Type, TypeVar, Union, Dict, Any, Set, AbstractSet
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from app.utils.convert import convert_objectid_to_str
from app.utils.objectid import ObjectId  # type: ignore
from pydantic import BaseModel, ValidationError
from pymongo.collection import Collection  
from app.utils.convert import convert_serializable
import logging


logger = logging.getLogger(__name__)

T = TypeVar("SchemaType", bound=BaseModel) # for schema 
R = TypeVar("DtoType", bound=BaseModel) # for dto
M = TypeVar("ModelType", bound=BaseModel) # for general model

class ConversionStrategy(Enum):
    SKIP_INVALID = "skip_invalid"
    RAISE_ON_INVALID = "raise_on_invalid"
    LOG_AND_SKIP = "log_and_skip"

class Context(Enum):
    LIST = "list"
    DICT = "dict"
    SET = "set"
    STR = "str"
    INT = "int"
    FLOAT = "float"
    NONE = "none"
    SINGLE = "single"

@dataclass(frozen=True)
class ModelUtilsConfig:
    DEFAULT_PROTECTED_FIELDS = frozenset({"id", "_id", "role", "created_at", "updated_at"})
    protected_fields: AbstractSet[str] = DEFAULT_PROTECTED_FIELDS
    conversion_strategy: ConversionStrategy = ConversionStrategy.RAISE_ON_INVALID
    log_conversion_failures: bool = True
    log_level: str = "WARNING"
    log_extra: Dict[str, Any] = field(default_factory=dict)

    def handle_error_and_log_or_raise(self, exc: AppBaseException) -> Any:
        strategy = self.conversion_strategy
        if strategy == ConversionStrategy.RAISE_ON_INVALID:
            raise exc
        elif strategy == ConversionStrategy.LOG_AND_SKIP:
            log_func = logger.error if exc.severity == ErrorSeverity.HIGH else logger.warning
            log_func(str(exc), extra=exc.to_dict())
            return self._get_default_value_for_context(exc.context)
        elif strategy == ConversionStrategy.SKIP_INVALID:
            return self._get_default_value_for_context(exc.context)
        else:
            # Handle unexpected strategy values
            logger.warning(f"Unknown conversion strategy: {strategy}, defaulting to RAISE_ON_INVALID")
            raise exc


    @staticmethod
    def _get_default_value_for_context(context: Context) -> Any:
        return {
            Context.LIST: [],
            Context.DICT: {},
            Context.SET: set(),
            Context.STR: "",
            Context.INT: 0,
            Context.FLOAT: 0.0,
            Context.NONE: None,
            Context.SINGLE: None
        }.get(context, None)


#* Abstract classes for model utils
class ModelConverter(ABC):
    @abstractmethod
    def convert_to_model(self, data: Dict[str, Any], model_class: Type[M]) -> Optional[M]:
        pass


#convert model to pydantic model
class ModelConverterImp(ModelConverter):
    def __init__(self, config: ModelUtilsConfig):
        self.config = config
            
    def convert_to_model(self, data: Dict[str, Any], model_class: Type[M]) -> Optional[M]:
        try:
            model = model_class.model_validate(data)
            return model
        except PydanticValidationError as e:
            field_errors = {str(err['loc'][0]): err['msg'] for err in e.errors()}
            raise PydanticBaseValidationError(
                message=f"Validation failed for {model_class.__name__}",
                field_errors=field_errors,
                hint="Invalid input fields. Please correct them.",
                cause=e,
                context=Context.SINGLE,
            )
        except Exception as e:
            app_exc = InternalServerError(
                message=f"Unexpected error during conversion to {model_class.__name__}",
                cause=e,
                context=Context.SINGLE,
            )
            return self.config.handle_error_and_log_or_raise(app_exc)

    def prepare_output_dto(self, data: Dict[str, Any], model_class: Type[R]) -> Optional[R]:
        data_str = convert_objectid_to_str(data)  
        data_http = convert_serializable(data_str)
        return model_class(**data_http)


    def convert_objectids_in_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
        return doc
#convert pydantic model to response model
class ModelResponseUtils:
    def __init__(self, config: Optional[ModelUtilsConfig] = None):
        self.config = config or ModelUtilsConfig()
        self._converter = ModelConverterImp(self.config)

    def to_response_model_dto(self, data: Dict[str, Any], model_class: Type[R]) -> Optional[R]:
        try:
            dto = self._converter.prepare_output_dto(data, model_class)
            logger.debug(f"Converted DTO: {dto}")
            return dto
        except PydanticValidationError as e:
            app_exc = PydanticBaseValidationError(
                message=f"Validation failed while converting to {model_class.__name__}",
                field_errors={str(err['loc'][0]): err['msg'] for err in e.errors()},
                cause=e,
                context=Context.SINGLE,
            )
            return self.config.handle_error_and_log_or_raise(app_exc)
        except Exception as e:
            app_exc = InternalServerError(
                message=f"Unexpected error during conversion to {model_class.__name__}",
                cause=e,
                context=Context.SINGLE,
            )
            return self.config.handle_error_and_log_or_raise(app_exc)

    
    def to_response_model_list_dto(self, data_list: List[Dict[str, Any]], model_class: Type[R]) -> List[R]:
        results = []
        for data in data_list:
            try:
                model = self.to_response_model_dto(data, model_class)
                if model is not None:
                    results.append(model)
                else:
                    logger.warning("Conversion failed for data", extra={"data": data})
                    continue
                
            except AppBaseException as e:
                app_exc = PydanticBaseValidationError(
                    message=f"Validation failed while converting to {model_class.__name__}",
                    field_errors={str(err['loc'][0]): err['msg'] for err in e.errors()},
                    cause=e,
                    context=Context.LIST,
                )
                raise self.config.handle_error_and_log_or_raise(app_exc)
            except Exception as e:
                app_exc = InternalServerError(
                    message="Unexpected error during conversion to response model list",
                    cause=e,
                    context=Context.LIST,
                )
                raise self.config.handle_error_and_log_or_raise(app_exc)
        return results
            

    
    def fetch_first_inserted(self, inserted_id: ObjectId, collection: Collection, model_class: Type[R]) -> Optional[R]:

        raw_doc = collection.find_one({"_id": inserted_id})

        if not raw_doc:
            raise NotFoundError(
                message="No document found with the given inserted id",
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
                status_code=404,
            )
        return self.to_response_model_dto(raw_doc, model_class)


#validate object id
class ObjectIdValidator:
    def __init__(self, config: Optional[ModelUtilsConfig] = None):
        self.config = config or ModelUtilsConfig()
        
    def validate(self, id_val: Union[str, ObjectId, None]) -> ObjectId:
        if id_val is None:
            app_exc = BadRequestError(
                message="ObjectId cannot be None",
                details={"received_value": None},
                context=Context.SINGLE,
            )
            return self.config.handle_error_and_log_or_raise(app_exc)
        if isinstance(id_val, ObjectId):
            return id_val
            
        if not isinstance(id_val, str):
            
            app_exc = BadRequestError(
                message="ObjectId must be a string or ObjectId",
                details={
                    "received_value": str(id_val),
                    "actual_type": type(id_val).__name__,
                    "expected_type": "str or ObjectId"
                },
                context=Context.SINGLE,
            )
            return self.config.handle_error_and_log_or_raise(app_exc)
        try:
            return ObjectId(id_val)
        except Exception as e:
            app_exc = BadRequestError(
                message="Invalid ObjectId format",
                cause=e,
                details={"input_value": id_val},
                context=Context.SINGLE,
            )
            return self.config.handle_error_and_log_or_raise(app_exc)

    

    def try_convert(self, id_val: Union[str, ObjectId, None]) -> Optional[ObjectId]:
        try:
            return self.validate(id_val)
        except BadRequestError:
            return None

#model utils
class ModelUtils:
    def __init__(self, config: Optional[ModelUtilsConfig] = None):
        self.config = config or ModelUtilsConfig()
        self._converter = ModelConverterImp(self.config)
        self._objectid_validator = ObjectIdValidator(self.config)
        self._response_utils = ModelResponseUtils(self.config)

    def to_model(self, data: Dict[str, Any], model_class: Type[M]) -> Optional[M]:
        if not self._is_valid_input_dict(data):
            app_exc = AppTypeError(
                message=f"Invalid input data for {model_class.__name__}",
                details={"received_value": data, "expected_type": "dict"},
                context=Context.DICT,
            )
            self.config.handle_error_and_log_or_raise(app_exc)
        return self._converter.convert_to_model(data, model_class)    

    
    def to_model_list(
        self, 
        data_list: Optional[List[Dict[str, Any]]], 
        model_class: Type[M]
    ) -> List[M]:

        if not isinstance(data_list, list):
            msg = f"Invalid input data for {model_class.__name__}: Expected list, got {type(data_list).__name__}"
            app_exc = PydanticBaseValidationError(
                message=msg,
                details={"received_value": data_list},
                context=Context.LIST,
            )
            self.config.handle_error_and_log_or_raise(app_exc)
        result: List[M] = []
        for data in data_list:
            model = self.to_model(data, model_class)
            if model is not None:
                result.append(model)
        return result
    
    def validate_object_id(self, id_val: Union[str, ObjectId, None]) -> ObjectId:
        return self._objectid_validator.validate(id_val)
    
    def try_convert_object_id(self, id_val: Union[str, ObjectId, None]) -> Optional[ObjectId]:
        return self._objectid_validator.try_convert(id_val)
        
    def prepare_safe_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not isinstance(update_data, dict):
                msg = f"Expected dict, got {type(update_data).__name__}"
                app_exc = PydanticBaseValidationError(
                    message=msg,
                    details={"received_value": update_data, "expected_type": "dict"},
                    context=Context.DICT,
                )
                raise self.config.handle_error_and_log_or_raise(app_exc)
            
            return {
                key: value for key, value in update_data.items()
                if key not in self.config.protected_fields
            }
        except PydanticValidationError as e:
            app_exc = PydanticBaseValidationError(
                message="Validation failed while preparing safe update",
                field_errors={str(err['loc'][0]): err['msg'] for err in e.errors()},
                cause=e,
                context=Context.DICT,
            )
            raise self.config.handle_error_and_log_or_raise(app_exc)
        except Exception as e:
            app_exc = InternalServerError(
                message="Unexpected error during preparing safe update",
                cause=e,
                details={"update_data": update_data},
                context=Context.DICT,
            )
            raise self.config.handle_error_and_log_or_raise(app_exc)



    def _is_valid_input_dict(self, data: Optional[Dict[str, Any]]) -> bool:
        return isinstance(data, dict)

    def convert_to_response_model_dto(self, data: Dict[str, Any], model_class: Type[R]) -> Optional[R]:
        return self._response_utils.to_response_model_dto(data, model_class)

    def convert_to_response_model_list_dto(self, data_list: List[Dict[str, Any]], model_class: Type[R]) -> List[R]:
        return self._response_utils.to_response_model_list_dto(data_list, model_class)

    def fetch_first_inserted(self, inserted_id: ObjectId, collection: Collection, model_class: Type[R]) -> Optional[R]:
        return self._response_utils.fetch_first_inserted(inserted_id, collection, model_class)



def create_model_utils(protected_fields: Optional[Set[str]] = None, strategy: ConversionStrategy = ConversionStrategy.RAISE_ON_INVALID) -> ModelUtils:
    config = ModelUtilsConfig(
        protected_fields=protected_fields or ModelUtilsConfig.DEFAULT_PROTECTED_FIELDS,
        conversion_strategy=strategy
    )

    return ModelUtils(config)



default_model_utils = create_model_utils()


