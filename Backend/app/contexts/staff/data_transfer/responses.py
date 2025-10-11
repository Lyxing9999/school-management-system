from app.place_holder import PlaceholderModel
from pydantic import RootModel
from typing import List
from pydantic import BaseModel
from app.contexts.shared.enum.roles import SystemRole
from datetime import datetime
from typing import Optional
class StaffBaseDataDTO(BaseModel):
    id: str
    user_id: Optional[str] = None
    staff_name: str
    staff_id: str
    role: SystemRole | None = None   
    phone_number: str | None = None  
    permissions: list[str] = []  
    created_at: datetime | None = None
    created_by: str | None = None
    updated_at: datetime | None = None
    deleted: bool = False
    deleted_by: str | None = None

    model_config = {
        "extra": "allow"
    }
class StaffReadDataDTO(StaffBaseDataDTO):   
    pass

class StaffReadDataDTOList(RootModel[List[StaffReadDataDTO]]):   
    pass




