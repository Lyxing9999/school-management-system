from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union, Type, TypeVar
from pymongo.database import Database, Collection
from app.utils.objectid import ObjectId 
from app.utils.model_utils import  create_model_utils, ModelUtils
from pydantic import BaseModel
T = TypeVar("T", bound=BaseModel)

class BaseServiceUtils: 
    def __init__(self, db: Database, model_class: Optional[Type[T]] = None, model_utils: Optional[ModelUtils] = None):
        self.db = db
        self.now = datetime.now(timezone.utc)
        self.model_utils = model_utils or create_model_utils()
        self.model_class = model_class

    def _to_model(self, data: Dict[str, Any]) -> Optional[T]:
        return self.model_utils.to_model(data, self.model_class)

    def _to_model_list(self, data_list: List[Dict[str, Any]]) -> List[T]:
        return self.model_utils.to_model_list(data_list, self.model_class)

    def _validate_objectid(self, id_val: Union[str, ObjectId]) -> Optional[ObjectId]:
        return self.model_utils.validate_object_id(id_val)

    def _prepare_safe_update(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.model_utils.prepare_safe_update(update_data)

    def to_response_model(self, data: Dict[str, Any]) -> Optional[T]:
        return self.model_utils.convert_to_response_model(data, self.model_class)

    def to_response_model_list(self, data_list: List[Dict[str, Any]]) -> List[T]:
        return self.model_utils.convert_to_response_model_list(data_list, self.model_class)
    
    def _fetch_first_inserted(self, inserted_id: ObjectId, collection: Collection) ->  Optional[T]:
        return self.model_utils.fetch_first_inserted(inserted_id, collection, self.model_class)  
    
    def get_now(self) -> datetime:
        return self.now