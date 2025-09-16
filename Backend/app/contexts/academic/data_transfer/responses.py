
from pydantic import BaseModel , RootModel
from typing import List
from app.contexts.common.base_entity_dto import Timestamps


class AcademicDeptUserDataDTO(BaseModel):
    id: str 
    email: str 
    username: str | None = None
    role: str 
    created_by_academic_dept: str | None = None
    timestamps: Timestamps | None = None
    deleted: bool | None = None
    deleted_by: str | None = None

    model_config = {
        "extra": "allow",
        "from_attributes": True     
    }


class AcademicFindAllByRoleDataDTO(AcademicDeptUserDataDTO):
    pass

class AcademicFindAllByRoleDataDTOList(RootModel[List[AcademicFindAllByRoleDataDTO]]):
    pass



from datetime import datetime

# -------------------------
# Class Data
# -------------------------
class AcademicFindAllClassDataDTO(BaseModel):
    id: str
    name: str
    grade: int
    owner: str | None = None
    owner_id: str | None = None
    homeroom_teacher: str | None = None
    subjects: List[str] | None = None
    students: List[str] | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted: bool | None = None
    deleted_at: datetime | None = None
    deleted_by: str | None = None

    model_config = {
        "extra": "allow",
        "from_attributes": True     
    }







# class ClassCreateDTO(BaseEntityDTO):
#     class_data: dict
#     pending_students: List[str]







# class ClassUpdateDTO(BaseEntityDTO):
#     name: str | None = None
#     grade: int | None = None
#     teacher_id: str | None = None
#     students: List[str] | None = None
#     courses: List[str] | None = None
#     status: ClassStatus | None = None
#     pending_students: List[str] | None = None
#     max_students: int | None = None





