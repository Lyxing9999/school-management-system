from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO , IAMUpdateDataDTO
from app.contexts.staff.data_transfer.responses import StaffReadDataDTO
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from typing import List, Optional

# =====================================================
# SECTION 1: USER MANAGEMENT (IAM)
# =====================================================
class PaginatedUsersDataDTO(BaseModel):
    users: List[IAMBaseDataDTO]
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
    deleted_at: datetime
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
    id: str
    staff_name: str
    model_config = {
        "extra": "ignore"
    }





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
    created_at: datetime
    updated_at: datetime
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
    created_at: datetime
    updated_at: datetime

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
    start_time: time
    end_time: time
    room: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AdminScheduleListDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[AdminScheduleSlotDataDTO]