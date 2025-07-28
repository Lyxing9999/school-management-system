from pydantic import BaseModel
from app.dtos.users.user_response_dto import UserResponseDTO
class UserLoginDataDTO(BaseModel):
    access_token: str
    user: UserResponseDTO


class UserLoginResponseDTO(BaseModel):
    data: UserLoginDataDTO
    message: str
    success: bool