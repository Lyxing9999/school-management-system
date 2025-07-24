from enum import Enum

class Role(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class FeedbackRole(str, Enum):
    STUDENT = Role.STUDENT.value
    TEACHER = Role.TEACHER.value

