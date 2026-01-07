from typing import List, Optional
from pydantic import Field

from app.contexts.school.data_transfer.responses import ClassSectionDTO

from .common import  ItemListDTO, OptionDTO, PaginatedDTO


class AdminClassDataDTO(ClassSectionDTO):
    subject_count: int = 0
    enrolled_count: int = 0
    homeroom_teacher_id: Optional[str] = None
    homeroom_teacher_name: Optional[str] = None
    subject_labels: List[str] = Field(default_factory=list)


class AdminClassListDTO(ItemListDTO[AdminClassDataDTO]):
    pass


class AdminClassSelectOptionDTO(OptionDTO):
    pass


class AdminClassSelectOptionListDTO(ItemListDTO[AdminClassSelectOptionDTO]):
    pass




class AdminClassPaginatedDTO(PaginatedDTO[AdminClassDataDTO]):
    pass