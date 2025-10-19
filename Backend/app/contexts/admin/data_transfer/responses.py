from pydantic import BaseModel 

from datetime import datetime
from app.contexts.shared.enum.roles import SystemRole
from app.contexts.iam.data_transfer.responses import IAMBaseDataDTO , IAMUpdateDataDTO
from app.contexts.staff.data_transfer.responses import StaffReadDataDTO
from app.contexts.shared.enum.roles import StaffRole
from app.contexts.student.data_transfer.responses import StudentInfoReadDataDTO
from typing import List


class AdminCreateUserDataDTO(IAMBaseDataDTO):
    pass

class AdminUpdateUserDataDTO(IAMUpdateDataDTO):
    pass


class AdminCreateStaffDataDTO(BaseModel):
    id: str
    user_id: str
    email: str
    username: str
    staff_id: str
    staff_name: str
    role: StaffRole
    phone_number: str
    permissions: List[str]
    address: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    deleted: bool
    deleted_by: str | None

    model_config = {
        "extra": "ignore"
    }
    

class PaginatedUsersDataDTO(BaseModel):
    users: List[IAMBaseDataDTO]
    total: int
    page: int
    page_size: int
    total_pages: int



class AdminGetStaffDataDTO(StaffReadDataDTO):
    model_config = {
        "extra": "forbid"
    }

class AdminGetStudentInfoDataDTO(StudentInfoReadDataDTO):
    pass

class AdminUpdateStaffDataDTO(StaffReadDataDTO):
    model_config = {
        "extra": "ignore"
    }






class AdminStaffSelectDTO(BaseModel):   
    id: str
    staff_name: str
    model_config = {
        "extra": "forbid"
    }


class AdminDeleteUserDTO(BaseModel):   
    id: str
    deleted_at: datetime
    deleted_by: str | None
    model_config = {
        "extra": "allow"
    }






class AdminCreateClassDTO(BaseModel):
    model_config = {
        "extra": "allow"
    }
    





