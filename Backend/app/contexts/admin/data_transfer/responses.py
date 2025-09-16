from pydantic import BaseModel 

from datetime import datetime

class PlaceholderModel(BaseModel):
    model_config = {
        "extra": "allow"  # allow extra fields
    }

    def __getattr__(self, item):
        # If attribute exists in extra fields, return it
        return self.model_dump().get(item, None)

class AdminCreateUserDataDTO(PlaceholderModel):
    model_config = {
        "extra": "allow"
    }

class AdminUpdateUserDataDTO(PlaceholderModel):
    model_config = {
        "extra": "allow"
    }




class AdminCreateClassDataDTO(PlaceholderModel):
    model_config = {
        "extra": "allow"
    }
    

class AdminDeleteUserDataDTO(BaseModel):   
    id: str
    deleted_at: datetime

class AdminStaffSelectDataDTO(BaseModel):   
    id: str
    staff_name: str
