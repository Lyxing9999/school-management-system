from pydantic import BaseModel
from app.contexts.shared.enum.roles import SystemRole
from bson import ObjectId
from typing import Optional
class StaffCreateSchema(BaseModel):
    staff_id: str
    staff_name: str
    role: SystemRole = SystemRole.TEACHER 
    user_id: str | None = None
    phone_number: str | None = None
    address: str | None = None
    created_by: str | None = None
    model_config = {
        "arbitrary_types_allowed": True,
        'extra': 'ignore'
    }


class StaffUpdateSchema(BaseModel):
    staff_id: str | None = None
    staff_name: str | None = None
    role: SystemRole | None = None

    phone_number: str | None = None
    address: str | None = None
    model_config = {
        "arbitrary_types_allowed": True,
        'extra': 'ignore'
    }
    