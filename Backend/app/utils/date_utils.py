from datetime import datetime # type: ignore
from typing import Any # type: ignore
import logging # type: ignore
from app.error.exceptions import BadRequestError, InternalServerError
from app.utils.objectid import ObjectId  # type: ignore

logger = logging.getLogger(__name__)
def ensure_date(value: Any) -> Any:
    """Ensure date is in correct format.

    - Converts ISO8601 strings to datetime
    - Converts datetime to ISO8601 string
    - Converts ObjectId to string
    Returns None if input is None.
    """
    if value is None:
        return None

    try:
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise BadRequestError(message="Invalid date format", details={"value": value}, user_message="The date format is invalid.")
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, ObjectId):
            return str(value)
        raise BadRequestError(message="Invalid date format", details={"value": value}, user_message="The date format is invalid.")
    except Exception as e:
        raise InternalServerError(message="Error ensuring date", cause=e)