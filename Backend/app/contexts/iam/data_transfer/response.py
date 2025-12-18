from typing import List
from pydantic import BaseModel, RootModel, ConfigDict
from app.contexts.shared.enum.roles import SystemRole
from datetime import datetime
from pydantic import ConfigDict
from app.contexts.shared.lifecycle.types import Status

# -------------------------
# Base User DTO
# -------------------------
class IAMBaseDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
        enum_values_as_str=True
    )
    id: str 
    email: str 
    role: SystemRole 
    username: str 
    status: Status 
    created_by: str 
    created_at: datetime 
    updated_at: datetime 
    deleted: bool | None = False 
    deleted_at: datetime | None  = None
    deleted_by: str | None = None 


# -------------------------
# Response DTO (login/register)
# -------------------------
class IAMResponseDataDTO(BaseModel):
    user: IAMBaseDataDTO
    access_token: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        populate_by_name=True
    )

# -------------------------
# Update DTO
# -------------------------
class IAMUpdateDataDTO(IAMBaseDataDTO):
    pass

# -------------------------
# Read DTO
# -------------------------
class IAMReadDataDTO(IAMBaseDataDTO):
    pass

class IAMReadDataDTOList(RootModel[List[IAMReadDataDTO]]):
    pass

class IAMSelectDataDTO(BaseModel):
    id: str
    email: str
    model_config =   {"extra": "allow"}
    
    