from typing import List
from bson import ObjectId
from datetime import datetime
from app.contexts.staff.models import Staff
from app.contexts.shared.enum.roles import StaffRole


class Academic(Staff):
    def __init__(
        self,
        staff_id: str,
        staff_name: str,
        phone_number: str,
        created_by: ObjectId,
        permissions: List[str],
        classes: List[ObjectId] | None = None,
        courses: List[ObjectId] | None = None,
        teachers: List[ObjectId] | None = None,
        attendance: List[ObjectId] | None = None,
        id: ObjectId | None = None,
        address: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        deleted_at: datetime | None = None,
        deleted: bool = False,
        deleted_by: ObjectId | None = None,
    ):
        super().__init__(
            staff_id=staff_id,
            staff_name=staff_name,
            role=StaffRole.ACADEMIC,
            phone_number=phone_number,
            created_by=created_by,
            id=id,
            permissions=permissions,
            address=address,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
            deleted_at=deleted_at,
            deleted=deleted,
            deleted_by=deleted_by
        )


        # Safe list initialization with ObjectId conversion and uniqueness
        self.classes: List[ObjectId] = list({ObjectId(x) for x in classes}) if classes else []
        self.courses: List[ObjectId] = list({ObjectId(x) for x in courses}) if courses else []
        self.teachers: List[ObjectId] = list({ObjectId(x) for x in teachers}) if teachers else []
        self.attendance: List[ObjectId] = list({ObjectId(x) for x in attendance}) if attendance else []
    # ----------------------- CRUD Helpers -----------------------
    def add_class(self, class_id: ObjectId):
        if class_id not in self.classes:
            self.classes.append(class_id)
            self.updated_at = datetime.utcnow()

    def remove_class(self, class_id: ObjectId):
        if class_id in self.classes:
            self.classes.remove(class_id)
            self.updated_at = datetime.utcnow()




    def add_course(self, course_id: ObjectId):
        if course_id not in self.courses:
            self.courses.append(course_id)
            self.updated_at = datetime.utcnow()

    def remove_course(self, course_id: ObjectId):
        if course_id in self.courses:
            self.courses.remove(course_id)
            self.updated_at = datetime.utcnow()

    def add_teacher(self, teacher_id: ObjectId):
        if teacher_id not in self.teachers:
            self.teachers.append(teacher_id)
            self.updated_at = datetime.utcnow()

    def remove_teacher(self, teacher_id: ObjectId):
        if teacher_id in self.teachers:
            self.teachers.remove(teacher_id)
            self.updated_at = datetime.utcnow()

    def add_attendance(self, attendance_id: ObjectId):
        if attendance_id not in self.attendance:
            self.attendance.append(attendance_id)
            self.updated_at = datetime.utcnow()






class AcademicFactory:
    pass


class AcademicMapper:
    @staticmethod
    def to_domain(data: dict) -> Academic:
        id_value = data.get("_id") or data.get("id")
        if id_value and not isinstance(id_value, ObjectId):
            id_value = ObjectId(id_value)

        role = data.get("role", StaffRole.ACADEMIC)
        role = Staff.validate_role(role)

        return Academic(
            staff_id=data["staff_id"],
            staff_name=data["staff_name"],
            phone_number=data.get("phone_number", ""),
            created_by=data["created_by"],
            academic=data.get("academic", ""),
            classes=data.get("classes", []),
            courses=data.get("courses", []),
            teachers=data.get("teachers", []),
            attendance=data.get("attendance", []),
            id=id_value,
            permissions=data.get("permissions", []),
            address=data.get("address"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deleted=data.get("deleted", False),
            deleted_at=data.get("deleted_at"),
            deleted_by=data.get("deleted_by"),
        )

    @staticmethod
    def to_persistence_dict(domain: Academic) -> dict:
        return {
            "_id": domain.id or ObjectId(),
            "staff_id": domain.staff_id,
            "staff_name": domain.staff_name,
            "academic": domain.academic,
            "classes": domain.classes,
            "courses": domain.courses,
            "teachers": domain.teachers,
            "attendance": domain.attendance,
            "phone_number": domain.phone_number,
            "address": domain.address,
            "permissions": domain.permissions,
            "created_by": domain.created_by,
            "created_at": domain.created_at,
            "updated_at": domain.updated_at,
            "deleted": domain.deleted,
            "deleted_at": domain.deleted_at,
            "deleted_by": domain.deleted_by,
            "role": domain.role.value,
        }

    @staticmethod
    def to_safe_dict(domain: Academic) -> dict:
        return {
            "id": str(domain.id) if domain.id else None,
            "staff_id": domain.staff_id,
            "staff_name": domain.staff_name,
            "academic": domain.academic,
            "classes": [str(x) for x in domain.classes],
            "courses": [str(x) for x in domain.courses],
            "teachers": [str(x) for x in domain.teachers],
            "attendance": [str(x) for x in domain.attendance],
            "phone_number": domain.phone_number,
            "address": domain.address,
            "permissions": domain.permissions,
            "created_by": str(domain.created_by) if domain.created_by else None,
            "created_at": domain.created_at,
            "updated_at": domain.updated_at,
            "deleted": domain.deleted,
            "deleted_at": domain.deleted_at,
            "deleted_by": str(domain.deleted_by) if domain.deleted_by else None,
            "role": domain.role.value,
        } 