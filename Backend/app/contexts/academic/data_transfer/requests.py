# from pydantic import BaseModel , Field , field_validator
# from app.contexts.academic_dept.error.academic_execptions import ClassCreateRequiredException
# from app.contexts.enum.class_enums import ClassStatus , ClassAttendance
# from typing import List
# class StudentInfo(BaseModel):
#     student_id: str
#     attendance: ClassAttendance
#     score: int

#     @field_validator("score")
#     def score_must_be_valid(cls, v):
#         if not 0 <= v <= 100:
#             raise ClassCreateRequiredException(v, "Score must be between 0 and 100")
#         return v


# class CourseInfo(BaseModel):
#     course_id: str | None = Field(None, min_length=24, max_length=24)
#     teacher_id: str = Field(..., min_length=24, max_length=24)  # required
#     schedule: List[str] = Field(default_factory=list)
#     max_students: int = Field(30)
#     status: ClassStatus = Field(ClassStatus.ACTIVE)

#     @field_validator("teacher_id")
#     def teacher_id_must_be_valid(cls, v):
#         if not v:
#             raise ClassCreateRequiredException(v, "Teacher ID is required")
#         if len(v) != 24:
#             raise ClassCreateRequiredException(v, "Teacher ID must be 24 characters")
#         return v

#     @field_validator("schedule")
#     def schedule_must_not_be_empty(cls, v):
#         if not v:
#             raise ClassCreateRequiredException(v, "Schedule is required")
#         return v


# class AcademicCreateCourseInfoSchema(CourseInfo):
#     pass

# class ClassCreateSchema(BaseModel):
#     name: str = Field(..., description="Class name")
#     grade: int = Field(..., description="Class grade")
#     teacher_id: str| None = Field(None, min_length=24, max_length=24, description="Teacher ID")
#     max_students: int | None = Field(30, description="Class max students")
#     status: ClassStatus | None = Field(ClassStatus.ACTIVE, description="Class status")
#     schedule: List[str] | None = Field([], description="Class schedule")
#     students: List[StudentInfo] | None = Field([], description="Pending students")
#     courses: List[CourseInfo] | None = Field([], description="Courses in this class")
#     created_by: str | None = Field(None, description="Created by")
#     @field_validator('grade', mode="after")
#     def grade_must_be_valid(cls, v):
#         if not 1 <= v <= 12:
#             raise ClassCreateRequiredException(v, "Grade must be between 1 and 12")
#         return v

#     @field_validator('max_students')
#     def max_students_must_be_valid(cls, v):
#         if v < 1:
#             raise ClassCreateRequiredException(v, "Max students must be greater than 0")
#         return v

from pydantic import BaseModel , field_validator , Field
from app.contexts.shared.enum.roles import UserRole , StaffRole
ALLOWED_ROLES = [StaffRole.TEACHER.value, UserRole.STUDENT.value]
from app.contexts.academic.error.academic_execptions import InvalidRoleToFindException
from typing import List
from datetime import datetime
class AcademicCreateUserSchema(BaseModel):
    email: str
    password: str
    username: str | None = None
    role: str | None = StaffRole.TEACHER.value
    created_by_academic_dept: str | None = None
    model_config = {
        "enum_values_as_str": True,
        "extra": "forbid"
    }
    @field_validator("role")
    def role_must_be_valid(cls, v):
        if v not in ALLOWED_ROLES:
            raise InvalidRoleToFindException(v)
        return v


    


class AcademicCreateClassSchema(BaseModel):
    name: str
    grade: int
    owner_id: str
    homeroom_teacher: str | None = None
    subjects: List[str] | None = None
    students: List[str] | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted: bool = False
    deleted_at: datetime | None = None
    model_config = {
        "enum_values_as_str": True,
        "extra": "forbid"
    }





class AcademicAddSubjectSchema(BaseModel):
    subjects: List[str]