from app.dtos.users.user_auth_dto import UserRegisterDataDTO
from app.dtos.users.user_base_dto import UserResponseDataDTO, UserResponseDataDTOList
from app.dtos.common.base_response_dto import BaseResponseDTO
from app.dtos.users.user_action_dto import UserUpdateData


class UserRegisterResponseDTO(BaseResponseDTO[UserRegisterDataDTO]):
    pass

class UserLoginResponseDTO(UserRegisterResponseDTO):
    pass


class UserUpdateResponseDTO(BaseResponseDTO[UserUpdateData]):
    pass


class UserResponseDTO(BaseResponseDTO[UserResponseDataDTO]):
    pass

class UserResponseDTOList(BaseResponseDTO[UserResponseDataDTOList]):
    pass





