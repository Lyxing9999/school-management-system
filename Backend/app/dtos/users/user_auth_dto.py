from pydantic import BaseModel
from app.dtos.users.user_action_dto import UserResponseDataDTO  

class UserRegisterDataDTO(BaseModel):
    access_token: str
    user: UserResponseDataDTO


class UserLoginDataDTO(UserRegisterDataDTO):
    pass





