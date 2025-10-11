from typing import List
from pydantic import BaseModel, RootModel
from app.contexts.shared.enum.roles import SystemRole
from datetime import datetime

# -------------------------
# Base User DTO
# -------------------------
class IAMBaseDTO(BaseModel):
    id: str | None = None
    email: str | None
    role: SystemRole
    username: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted: bool = False
    deleted_at: datetime | None = None
    deleted_by: str | None = None
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
        "enum_values_as_str": True
    }

# -------------------------
# Response DTO (login/register)
# -------------------------
class IAMResponseDTO(BaseModel):
    user: IAMBaseDTO
    access_token: str

    model_config = {"extra": "forbid",
    "populate_by_name": True}

# -------------------------
# Update DTO
# -------------------------
class IAMUpdateDataDTO(BaseModel):
    username: str | None = None
    email: str | None = None
    model_config = {"extra": "allow"}

# -------------------------
# Read DTO
# -------------------------
class IAMReadDataDTO(IAMBaseDTO):
    pass

class IAMReadDataDTOList(RootModel[List[IAMReadDataDTO]]):
    pass

class IAMSelectDataDTO(BaseModel):
    id: str
    email: str
    model_config =   {"extra": "allow"}
    
    