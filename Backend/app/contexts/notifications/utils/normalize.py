import datetime as dt
from typing import Any
from bson import ObjectId

def normalize_value(v: Any) -> Any:
    # primitives
    if v is None or isinstance(v, (str, int, float, bool)):
        return v

    # mongo ids
    if isinstance(v, ObjectId):
        return str(v)

    # datetime/date/time
    if isinstance(v, dt.datetime):
        return v.isoformat()
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, dt.time):
        return v.strftime("%H:%M")  # best for schedules

    # containers
    if isinstance(v, dict):
        return {str(k): normalize_value(val) for k, val in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [normalize_value(x) for x in v]

    # fallback: enums, Decimal, custom objects
    return str(v)