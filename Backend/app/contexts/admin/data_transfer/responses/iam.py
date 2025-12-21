from pydantic import  ConfigDict

from app.contexts.iam.data_transfer.response import IAMBaseDataDTO, IAMUpdateDataDTO
from app.contexts.iam.domain.iam import IAMStatus

from .common import BaseDTO, PaginatedDTO

class PaginatedUserItemDTO(IAMBaseDataDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)
    created_by_name: str


class PaginatedUsersDataDTO(PaginatedDTO[PaginatedUserItemDTO]):
    pass


class AdminCreateUserDataDTO(IAMBaseDataDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)


class AdminUpdateUserDataDTO(IAMUpdateDataDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)


class AdminSetUserStatusDTO(BaseDTO):
    status: IAMStatus


class AdminDeleteUserDTO(BaseDTO):
    id: str


class AdminHardDeleteUserDTO(BaseDTO):
    id: str
    deleted: bool