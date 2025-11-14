from pydantic import BaseModel 

from datetime import datetime
from app.contexts.shared.enum.roles import SystemRole
from app.contexts.iam.data_transfer.responses import IAMBaseDataDTO , IAMUpdateDataDTO
from app.contexts.staff.data_transfer.responses import StaffReadDataDTO
from app.contexts.shared.enum.roles import StaffRole
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from app.contexts.student.data_transfer.responses import StudentInfoReadDataDTO
from typing import List

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



# =====================================================
# SECTION 3: STUDENT MANAGEMENT
# =====================================================
class AdminGetStudentInfoDataDTO(StudentInfoReadDataDTO):
    pass


class AdminCreateClassDTO(BaseModel):
    model_config = {
        "extra": "allow"
    }
    






