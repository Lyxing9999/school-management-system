
from pydantic import BaseModel , RootModel
from typing import List


from app.contexts.admin.data_transfer.response import IAMBaseDataDTO
from app.contexts.admin.data_transfer.response import PaginatedUsersDataDTO

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





class AcademicStaffNameSelectDTO(BaseModel):
    user_id: str | None = None
    staff_name: str | None = None


class AcademicGetStudentInfoDataDTO(StudentInfoReadDataDTO):
    pass


class AcademicStudentsPageDTO(PaginatedUsersDataDTO):
    pass
class AcademicCreateStudentDTO(IAMBaseDataDTO):
    pass



class AcademicUpdateUserDTO(IAMBaseDataDTO):
    pass

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





