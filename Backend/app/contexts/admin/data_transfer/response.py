from pydantic import BaseModel, ConfigDict

from app.contexts.iam.data_transfer.response import IAMBaseDataDTO , IAMUpdateDataDTO
from app.contexts.staff.data_transfer.responses import StaffReadDataDTO
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from typing import List, Optional
import datetime as dt
# =====================================================
# SECTION 1: USER MANAGEMENT (IAM)
# =====================================================
class PaginatedUserItemDTO(IAMBaseDataDTO):
    created_by_name: str
    
class PaginatedUsersDataDTO(BaseModel):
    users: List[PaginatedUserItemDTO]
    total: int
    page: int
    page_size: int
    total_pages: int

class AdminCreateUserDataDTO(IAMBaseDataDTO):
    pass

class AdminUpdateUserDataDTO(IAMUpdateDataDTO):
    pass


class AdminDeleteUserDTO(BaseModel):   
    id: str
    deleted_at: dt.datetime
    deleted_by: str | None
    model_config = {
        "extra": "allow"
    }

class AdminHardDeleteUserDTO(BaseModel):
    id: str
    deleted: bool
    model_config = {
        "extra": "allow"
    }
# =====================================================
# SECTION 2: STAFF MANAGEMENT
# =====================================================
class AdminGetStaffDataDTO(StaffReadDataDTO):
    pass
class AdminCreateStaffDataDTO(StaffBaseDataDTO):
    pass
class AdminUpdateStaffDataDTO(StaffBaseDataDTO):
    pass
class AdminStaffNameSelectDTO(BaseModel):
    user_id: str
    staff_name: str
    model_config = {
        "extra": "ignore",
    }

class AdminTeacherSelectDTO(AdminStaffNameSelectDTO):
    pass

class AdminTeacherListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[AdminTeacherSelectDTO]




class AdminCreateClassDTO(BaseModel):
    model_config = {
        "extra": "allow"
    }
    


# =====================================================
# SECTION 4: CLASS MANAGEMENT
# =====================================================

class AdminClassDataDTO(BaseModel):
    id: str
    name: str
    teacher_id: Optional[str]
    student_ids: List[str]
    subject_ids: List[str]
    max_students: Optional[int]
    created_at: dt.datetime
    updated_at: dt.datetime
    deleted: bool

class AdminClassListDTO(BaseModel):
    items: List[AdminClassDataDTO]

# =====================================================
# SECTION 5: SUBJECT MANAGEMENT
# =====================================================

class AdminSubjectDataDTO(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str]
    allowed_grade_levels: List[int]
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime

class AdminSubjectListDTO(BaseModel):
    items: List[AdminSubjectDataDTO]


# =====================================================
# SECTION 6: SCHEDULE MANAGEMENT
# =====================================================
class AdminScheduleSlotDataDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    class_id: str
    teacher_id: str
    day_of_week: int
    start_time: dt.time             
    end_time: dt.time 
    room: str | None = None
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None


class AdminScheduleListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[AdminScheduleSlotDataDTO]


# =====================================================
# Student Management
# =====================================================

class AdminStudentNameSelectDTO(BaseModel):
    id: str
    username: str
    model_config = {
        "extra": "ignore"
    }


class AdminStudentNameSelectListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: List[AdminStudentNameSelectDTO]