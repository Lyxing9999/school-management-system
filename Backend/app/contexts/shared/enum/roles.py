from enum import Enum

class SystemRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"
    # ACADEMIC = "academic"
    # Optional future roles:
    # HR = "hr"
    # FRONT_OFFICE = "front_office"
    # FINANCE = "finance"
    # PARENT = "parent"




class UserRole(str, Enum):
    STUDENT = "student"
    # PARENT = "parent"

class StaffRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    ACADEMIC = "academic"
    # FRONT_OFFICE = "front_office"
    # FINANCE = "finance"
    # HR = "hr"