from typing import List, Optional
from pydantic import BaseModel, RootModel, ConfigDict

from app.contexts.shared.lifecycle.dto import LifecycleDTO


# -------------------------
# Base User DTO (API-facing)
# -------------------------
class IAMBaseDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: str
    email: str
    role: str               
    username: Optional[str] = None
    status: str              
    created_by: Optional[str] = None
    lifecycle: LifecycleDTO


# -------------------------
# Response DTO (login/register)
# Shape: {"user": {...}, "access_token": "..."}
# -------------------------
class IAMResponseDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        populate_by_name=True,
    )

    user: IAMBaseDataDTO
    access_token: str


# -------------------------
# Update / Read DTOs
# -------------------------
class IAMUpdateDataDTO(IAMBaseDataDTO):
    pass


class IAMReadDataDTO(IAMBaseDataDTO):
    pass


class IAMReadDataDTOList(RootModel[List[IAMReadDataDTO]]):
    pass


# -------------------------
# Select DTO (dropdown etc.)
# -------------------------
class IAMSelectDataDTO(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    email: str