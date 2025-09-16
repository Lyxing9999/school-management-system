
from pydantic import BaseModel
class PlaceholderModel(BaseModel):
    model_config = {
        "extra": "allow"  # allow extra fields
    }

    def __getattr__(self, item):
        # If attribute exists in extra fields, return it
        return self.model_dump().get(item, None)

    

class ClassCreateDataDTO(PlaceholderModel):
    pass

class ClassUpdateDataDTO(PlaceholderModel):
    pass

class ClassDeleteDataDTO(PlaceholderModel):
    pass



class ClassAssignTeacherDataDTO(PlaceholderModel):
    pass


# read dto
class ClassReadDataDTO(PlaceholderModel):
    pass

