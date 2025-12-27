from typing import List, Optional
from pydantic import Field

from app.contexts.school.data_transfer.responses import ClassSectionDTO

from .common import  ItemListDTO, NameSelectDTO


class AdminClassDataDTO(ClassSectionDTO):
    subject_count: int = 0
    enrolled_count: int = 0
    teacher_id: Optional[str] = None
    teacher_name: Optional[str] = None
    subject_labels: List[str] = Field(default_factory=list)


class AdminClassListDTO(ItemListDTO[AdminClassDataDTO]):
    pass


class AdminClassSelectDTO(NameSelectDTO):
    pass


class AdminClassSelectListDTO(ItemListDTO[AdminClassSelectDTO]):
    pass



