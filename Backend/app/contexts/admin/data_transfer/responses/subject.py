
from typing import Optional, List
from app.contexts.school.data_transfer.responses import SubjectDTO
from .common import BaseDTO, LifecycleDTO, PaginatedDTO, OptionDTO, ItemListDTO



class AdminSubjectDataDTO(SubjectDTO):
    """
    Admin version of SubjectDTO:
    - includes lifecycle metadata if present in Mongo doc
    """
    lifecycle: Optional[LifecycleDTO] = None


class AdminSubjectPaginatedDTO(PaginatedDTO[AdminSubjectDataDTO]):
    """
    Paginated response for admin subject list endpoints.
    """
    pass

class AdminSubjectListDTO(List[AdminSubjectDataDTO]):
    """
    Paginated response for admin subject list endpoints.
    """
    pass

class AdminSubjectNameSelectDTO(OptionDTO):
    """
    Lightweight (id, name) projection for selects/dropdowns.
    """
    pass

class AdminSubjectNameSelectListDTO(ItemListDTO[AdminSubjectNameSelectDTO]):
    pass


