from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# -------------------------
# Login
# -------------------------
class IAMLoginSchema(BaseModel):
    email: str
    password: str 


# -------------------------
# Update
# -------------------------
class IAMUpdateSchema(BaseModel):
    username: str | None =  None
    email: str | None = None
    password: str | None = None
    model_config = {
         "enum_values_as_str": True,
    }


class IAMMeUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(default=None, max_length=50)


class PasswordResetConfirmSchema(BaseModel):
    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8)