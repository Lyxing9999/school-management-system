from pydantic import BaseModel, Field
from app.contexts.shared.enum.roles import SystemRole, UserRole , StaffRole
from typing import Optional , List
from app.contexts.iam.data_transfer.request import IAMUpdateSchema
from app.contexts.staff.data_transfer.requests import StaffUpdateSchema
from app.contexts.student.data_transfer.requests import StudentInfoUpdateSchema
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
# SECTION 3: STUDENT MANAGEMENT
# =====================================================
class AdminUpdateInfoStudentSchema(StudentInfoUpdateSchema):
    pass


# =====================================================
# SECTION 4: SCHOOL MANAGEMENT Class
# =====================================================
class AdminCreateClassSchema(BaseModel):
    name: str
    max_students: int
    grade: int
    status: bool
    class_room: Optional[str] = None
    homeroom_teacher: Optional[str] = None
    subjects: Optional[List[str]] = None
    students: Optional[List[str]] = None
    model_config = {
        "extra": "allow"
    }

# class AdminUpdateClassSchema(SchoolClassUpdateSchema):
#     pass

# =====================================================
# SECTION 5: SCHOOL MANAGEMENT Subject
# =====================================================
# class AdminCreateSubjectSchema(SubjectCreateSchema):
#     pass

# class AdminUpdateSubjectSchema(SubjectUpdateSchema):
#     pass