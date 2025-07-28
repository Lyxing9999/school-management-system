from pydantic import BaseModel

class UserRegisterDataDTO(BaseModel):
    access_token: str

class UserRegisterResponseDTO(BaseModel):
    data: UserRegisterDataDTO
    message: str
    success: bool