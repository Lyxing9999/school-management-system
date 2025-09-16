from pydantic import BaseModel
from app.contexts.shared.enum.roles import StaffRole
from bson import ObjectId

class StaffCreateRequestSchema(BaseModel):
    staff_id: str
    staff_name: str
    role: StaffRole
    phone_number: str
    address: str | None = None



class StaffUpdateRequestSchema(BaseModel):
    staff_id: str | ObjectId | None = None
    staff_name: str | None = None
    role: StaffRole | None = None
    phone_number: str | None = None
    created_by: ObjectId | None = None
    model_config = {
        "arbitrary_types_allowed": True 
    }
    