
from pydantic import RootModel ,ConfigDict 
from typing import List
from pydantic import BaseModel
from app.contexts.shared.enum.roles import SystemRole
from datetime import datetime
from typing import Optional

class StaffBaseDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        enum_values_as_str=True

    )
    id: str
    user_id: Optional[str] = None
    staff_name: str
    staff_id: str
    role: SystemRole
    phone_number: str | None = None  
    permissions: list[str] = []  
    address: str | None = None
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    deleted: bool = False
    deleted_by: str | None = None


class StaffReadDataDTO(StaffBaseDataDTO):   
    pass

class StaffReadDataDTOList(RootModel[List[StaffReadDataDTO]]):   
    pass




