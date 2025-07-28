# app/dtos/feedback_response_dto.py
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class FeedbackRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class FeedbackCategory(str, Enum):
    BUG = "bug"
    SUGGESTION = "suggestion"
    INQUIRY = "inquiry"
    OTHER = "other"

class FeedbackStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    CLOSED = "closed"

class FeedbackResponse(BaseModel):
    responder_id: str  # ref to users._id
    message: str
    responded_at: int  # Unix timestamp

class FeedbackResponseDTO(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    role: FeedbackRole
    category: FeedbackCategory
    message: str
    status: FeedbackStatus
    response: Optional[FeedbackResponse] = None
    created_at: int  # Unix timestamp

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str,
        }
    }

class FeedbackListResponseDTO(BaseModel):
    feedbacks: List[FeedbackResponseDTO]

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
    }