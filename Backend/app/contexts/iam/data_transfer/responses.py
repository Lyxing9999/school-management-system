from typing import List
from pydantic import BaseModel, RootModel , Field
from app.contexts.common.base_entity_dto import Timestamps
from datetime import datetime

# -------------------------
# User DTOs
# -------------------------
class UserResponseDataDTO(BaseModel):
    model_config = {
        "extra": "allow",  # accept all fields
    }


class UserResponseDataDTOList(RootModel[List[UserResponseDataDTO]]):
    pass

# -------------------------
# Action DTOs
# -------------------------
class UserLoginDataDTO(BaseModel):
    access_token: str
    user: UserResponseDataDTO

    model_config = {
        "extra": "forbid"
    }

class UserRegisterDataDTO(BaseModel):
    access_token: str
    user: UserResponseDataDTO

    model_config = {
        "extra": "forbid"
    }




# -------------------------
# Update / Select DTOs
# -------------------------
class UserSelectDataDTO(BaseModel):
    id: str  
    username: str | None =  None
    email: str | None =  None

    model_config = {
        "extra": "ignore",

    }
class UserSelectDataDTOList(RootModel[List[UserSelectDataDTO]]):
    pass

class UserUpdateDataDTO(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None

    model_config = {
        "extra": "ignore",
    }


# -------------------------
# Read DTOs
# -------------------------
from app.place_holder import PlaceholderModel
class UserReadDataDTO(PlaceholderModel):
    # Placeholder, accept any raw data
    model_config = {
        "extra": "allow",  # accept all fields
    }
class UserReadDataDTOList(RootModel[List[UserReadDataDTO]]):
    pass
    