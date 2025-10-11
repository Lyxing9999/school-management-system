from app.place_holder import PlaceholderModel
from pydantic import BaseModel
from bson.objectid import ObjectId
from typing import List



class ClassCreateRequestSchema(BaseModel):
    name: str
    grade: int
    max_students: int
    status: bool
    created_by: ObjectId
    homeroom_teacher: ObjectId | None = None
    subjects: List[ObjectId] | None = None
    students: List[ObjectId] | None = None
    model_config = {
        "arbitrary_types_allowed": True
    }

class ClassUpdateRequestSchema(PlaceholderModel):
    pass




# -------------------------
# Assign Teacher
# -------------------------
class ClassAssignTeacherRequestSchema(PlaceholderModel):
    pass

class ClassRemoveTeacherRequestSchema(PlaceholderModel):
    pass



# -------------------------
# Student
# -------------------------

class ClassAddStudentRequestSchema(PlaceholderModel):
    pass

class ClassRemoveStudentRequestSchema(PlaceholderModel):
    pass
 



# -------------------------
# Subject
# -------------------------
class ClassAssignSubjectRequestSchema(PlaceholderModel):
    pass

class ClassRemoveSubjectRequestSchema(PlaceholderModel):
    pass


# -------------------------
# Delete
# -------------------------




class ClassDeleteRequestSchema(PlaceholderModel):
    pass