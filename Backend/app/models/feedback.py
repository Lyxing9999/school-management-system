from pydantic import BaseModel, Field # type: ignore
from datetime import datetime, timezone
from app.enums.roles import FeedbackRole
from app.enums.category import Category
from app.enums.status import FeedbackStatus
from app.utils.pyobjectid import PyObjectId
from typing import ClassVar

class FeedbackResponseModel(BaseModel):
    _collection_name: ClassVar[str] = "feedback_response"
    id: PyObjectId | None = Field(None, alias="_id")
    responder_id: str | None = None
    message: str | None = None
    responded_at: datetime | None = None


class FeedbackModel(BaseModel):
    id: PyObjectId | None = Field(default=None, alias="_id")
    sender_id: str
    receiver_id: str | None = None
    role: FeedbackRole
    category: Category
    message: str = Field(..., min_length=5, max_length=1000)
    status: FeedbackStatus | None = None
    response: FeedbackResponseModel | None = None
    created_at: datetime | None = None
    model_config = {
        "extra": "ignore",
        "from_attributes": True,
        "populate_by_name": True,
        "use_enum_values": True,
        "arbitrary_types_allowed": True, 
        "json_encoders": {

            PyObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        }
    }
