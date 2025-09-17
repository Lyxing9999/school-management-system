from pydantic import BaseModel 

from datetime import datetime
from app.contexts.shared.enum.roles import SystemRole
class AdminBaseUserDataDTO(BaseModel):
    id: str
    username: str | None
    email: str
    role: SystemRole 
    created_at: datetime
    created_by: str  | None 
    updated_at: datetime  | None
    deleted: bool 
    deleted_by: str | None
    model_config = {
        "extra": "allow"
    }

class AdminCreateUserDataDTO(AdminBaseUserDataDTO):
    model_config = {
        "extra": "allow"
    }

class AdminUpdateUserDataDTO(AdminBaseUserDataDTO):
    model_config = {
        "extra": "allow"
    }

class AdminCreateClassDataDTO(BaseModel):
    model_config = {
        "extra": "allow"
    }
    

class AdminDeleteUserDataDTO(BaseModel):   
    id: str
    deleted_at: datetime
    deleted_by: str | None
    model_config = {
        "extra": "allow"
    }

class AdminStaffSelectDataDTO(BaseModel):   
    id: str
    staff_name: str
    model_config = {
        "extra": "allow"
    }
