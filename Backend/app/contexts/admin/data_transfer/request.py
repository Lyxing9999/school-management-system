from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.contexts.shared.enum.roles import SystemRole, StaffRole
from typing import Optional , List
from app.contexts.iam.data_transfer.request import IAMUpdateSchema
from app.contexts.staff.data_transfer.requests import StaffUpdateSchema
from app.contexts.school.domain.schedule import DayOfWeek
# from app.contexts.schools.data_transfer.requests.class_requests import SchoolClassUpdateSchema
# from app.contexts.schools.data_transfer.requests.subject_requests import SubjectCreateSchema, SubjectUpdateSchema



# =====================================================
# SECTION 1: USER MANAGEMENT (IAM)
# =====================================================

class AdminCreateUserSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    role: SystemRole 
    created_by: Optional[str] = None
    model_config = {"use_enum_values": True}

class AdminUpdateUserSchema(IAMUpdateSchema):
    pass

# =====================================================
# SECTION 2: STAFF MANAGEMENT
# =====================================================
class AdminCreateStaffSchema(BaseModel):
    staff_id: str
    staff_name: str
    phone_number: str
    user_id: Optional[str] = None
    address: Optional[str] = None

    # IAM fields (optional if staff is being created for an existing IAM user)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    permission: Optional[str] = None
    role: StaffRole
    created_by: Optional[str] = None


class AdminUpdateStaffSchema(StaffUpdateSchema):
    pass




# =====================================================
# SECTION 4: SCHOOL MANAGEMENT Class
# =====================================================
class AdminCreateClassSchema(BaseModel):
    name: str = Field(..., min_length=1)
    teacher_id: Optional[str] = None
    subject_ids: Optional[List[str]] = None
    max_students: Optional[int] = Field(default=None, ge=1)

    @field_validator("name")
    def strip_name(cls, v: str) -> str:
        return v.strip()


class AdminAssignTeacherToClassSchema(BaseModel):
    teacher_id: str = Field(..., min_length=1)


class AdminEnrollStudentToClassSchema(BaseModel):
    student_id: str = Field(..., min_length=1)


class AdminCreateSubjectSchema(BaseModel):
    name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    description: Optional[str] = None
    allowed_grade_levels: Optional[List[int]] = None

    @field_validator("name", "code")
    def strip_fields(cls, v: str) -> str:
        return v.strip()


# =====================================================
# SECTION 3: SCHOOL MANAGEMENT Schedule
# =====================================================
class AdminCreateScheduleSlotSchema(BaseModel):
    """
    Request body for admin creating a schedule slot.
    """
    model_config = ConfigDict(from_attributes=True)

    class_id: str = Field(..., description="ClassSection ObjectId as string")
    teacher_id: str = Field(..., description="Teacher IAM/Staff ObjectId as string")
    day_of_week: DayOfWeek | int = Field(..., description="1=Mon .. 7=Sun")
    start_time: time
    end_time: time
    room: Optional[str] = None


class AdminUpdateScheduleSlotSchema(BaseModel):
    """
    Request body for admin updating an existing schedule slot.
    All fields required for simplicity; you can make them Optional if partial updates.
    """
    model_config = ConfigDict(from_attributes=True)

    day_of_week: DayOfWeek | int
    start_time: time
    end_time: time
    room: Optional[str] = None