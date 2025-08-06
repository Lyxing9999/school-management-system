from app.dtos.common.base_response_dto import BaseResponseDTO
from app.dtos.classes.admin_class_dto import AdminClassCreateDataDTO, AdminClassUpdateDataDTO, AdminClassDeleteDataDTO


class AdminClassCreateResponseDTO(BaseResponseDTO[AdminClassCreateDataDTO]):
    pass
    



class AdminClassUpdateResponseDTO(BaseResponseDTO[AdminClassUpdateDataDTO]):
    pass
    

class AdminClassDeleteResponseDTO(BaseResponseDTO[AdminClassDeleteDataDTO]):
    pass