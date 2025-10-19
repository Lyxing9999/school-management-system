
from app.place_holder import PlaceholderModel
from pydantic import BaseModel, Field
from bson.objectid import ObjectId
from typing import List



class SchoolClassCreateSchema(BaseModel):
    name: str 
    grade: int
    max_students: int
    status: bool
    code: str | None = None
    academic_year: str | None = None
    class_room: str | None = None
    created_by: str | None = None
    homeroom_teacher: ObjectId | None = None
    subjects: List[str] | None = None
    students: List[str] | None = None
    model_config = {
        "arbitrary_types_allowed": True
    }





class SchoolClassUpdateSchema(BaseModel):
    name: str | None = None
    grade: int | None = None
    max_students: int | None = None
    status: bool | None = None
    code: str | None = None
    academic_year: str | None = None
    class_room: str | None = None
    created_by: str | None = None
    homeroom_teacher: ObjectId | None = None
    subjects: List[str] | None = None
    students: List[str] | None = None
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