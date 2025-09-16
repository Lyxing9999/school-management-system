from app.place_holder import PlaceholderModel
from pydantic import RootModel
from typing import List
from pydantic import BaseModel

class StaffReadDataDTO(PlaceholderModel):   
    pass

class StaffReadDataDTOList(RootModel[List[StaffReadDataDTO]]):   
    pass




