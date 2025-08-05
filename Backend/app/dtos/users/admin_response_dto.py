
from app.dtos.common.base_response_dto import BaseResponseDTO
from app.dtos.users.admin_user_dto import AdminCreateUserDataDTO, AdminUpdateUserDataDTO, AdminDeleteUserDataDTO, AdminFindUserDataDTO, AdminFindUserDataListDTO


class AdminCreateUserResponseDTO(BaseResponseDTO[AdminCreateUserDataDTO]):
    pass

class AdminUpdateUserResponseDTO(BaseResponseDTO[AdminUpdateUserDataDTO]):
    pass

class AdminDeleteUserResponseDTO(BaseResponseDTO[AdminDeleteUserDataDTO]):
    pass

class AdminFindUserResponseDTO(BaseResponseDTO[AdminFindUserDataDTO]):
    pass


class AdminFindUserResponseDTOList(BaseResponseDTO[AdminFindUserDataListDTO]):
    pass