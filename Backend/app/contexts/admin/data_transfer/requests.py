from pydantic import BaseModel, Field
from app.contexts.shared.enum.roles import SystemRole, UserRole , StaffRole
from app.place_holder import PlaceholderModel
from typing import Optional , List
from app.contexts.iam.data_transfer.requests import IAMUpdateSchema
from app.contexts.staff.data_transfer.requests import StaffCreateRequestSchema, StaffUpdateRequestSchema


class AdminCreateUserSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    role: SystemRole 
    created_by: Optional[str] = None

class AdminCreateStaffSchema(BaseModel):
    staff_id: str
    staff_name: str
    phone_number: str
    user_id: Optional[str] = None
    address: Optional[str] = None

    # IAM fields (optional if staff is being created for an existing IAM user)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    permission: Optional[str] = None
    role: StaffRole
    created_by: Optional[str] = None


class AdminUpdateUserSchema(IAMUpdateSchema):
    pass

class AdminUpdateStaffSchema(StaffUpdateRequestSchema):
    pass





class AdminCreateClassSchema(PlaceholderModel):
    #todo 
    pass