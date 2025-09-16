from enum import Enum

class SystemRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    FRONT_OFFICE = "front_office"
    FINANCE = "finance"
    STUDENT = "student"
    PARENT = "parent"
    ACADEMIC = "academic"
    HR = "hr"
    




class UserRole(str, Enum):
    STUDENT = "student"
    PARENT = "parent"

class StaffRole(str, Enum):
    TEACHER = "teacher"
    FRONT_OFFICE = "front_office"
    FINANCE = "finance"
    ACADEMIC = "academic"
    HR = "hr"