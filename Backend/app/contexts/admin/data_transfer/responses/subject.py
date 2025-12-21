from typing import List, Optional

from pydantic import Field
from app.contexts.school.data_transfer.responses import SubjectDTO

from .common import ItemListDTO, NameSelectDTO


class AdminSubjectDataDTO(SubjectDTO):
    pass

class AdminSubjectListDTO(ItemListDTO[AdminSubjectDataDTO]):
    pass


class AdminSubjectNameSelectDTO(NameSelectDTO):
    pass


class AdminSubjectNameSelectListDTO(ItemListDTO[AdminSubjectNameSelectDTO]):
    pass