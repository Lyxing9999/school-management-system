from typing import Any, Dict
from bson import ObjectId
from pydantic import HttpUrl
from datetime import datetime



def convert_objectid_to_str(data: Any) -> Dict[str, Any]:
    if isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(i) for i in data]
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, HttpUrl):
        return str(data)
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data




def convert_serializable(obj):
    if isinstance(obj, dict):
        return {k: convert_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_serializable(i) for i in obj]
    elif isinstance(obj, (ObjectId, HttpUrl)):
        return str(obj)
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj