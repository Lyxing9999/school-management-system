from pydantic import BaseModel

class UserUpdateResponseDataDTO(BaseModel):
    username: str | None
    email: str | None


class UserUpdateResponseDTO(BaseModel):
    data: UserUpdateResponseDataDTO
    message: str
    success: bool

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
    }