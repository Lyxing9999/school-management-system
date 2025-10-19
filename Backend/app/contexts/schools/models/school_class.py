from datetime import datetime
from typing import List
from bson import ObjectId
from app.contexts.schools.data_transfer.requests.class_requests import SchoolClassCreateSchema
from app.contexts.schools.data_transfer.responses.class_responses import SchoolClassBaseDataDTO
from app.contexts.schools.error.school_exceptions import ClassFullException, ClassUpdateException
from typing import Optional 

# -------------------------
# Domain Model
# -------------------------

class SchoolClass:
    def __init__(
        self,
        name: str,
        grade: int,
        max_students: int,
        status: bool,
        id: Optional[ObjectId] = None,
        code: Optional[str] = None,
        academic_year: Optional[str] = None,
        class_room: Optional[str] = None,
        homeroom_teacher: Optional[ObjectId] = None,
        created_by: Optional[ObjectId] = None,
        students: Optional[List[ObjectId]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted: bool = False,
        deleted_at: Optional[datetime] = None
    ):
        self.id = id or ObjectId()
        self.name = name
        self.grade = grade
        self.max_students = max_students
        self.status = bool(status)
        self.code = code or f"CLS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        self.academic_year = academic_year or f"{datetime.utcnow().year}-{datetime.utcnow().year + 1}"
        self.class_room = class_room
        self.homeroom_teacher = homeroom_teacher  # 1 teacher per class
        self.students = students or []
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted
        self.deleted_at = deleted_at

    # -------------------------
    # Business Logic Methods
    # -------------------------
    def is_full(self) -> bool:
        return len(self.students) >= self.max_students

    

    def add_student(self, student_id: ObjectId):
        if self.is_full():
            raise ClassFullException(self.max_students)
        if student_id in self.students:
            raise ClassUpdateException(str(self.id), "add student", "Student already in class")
        self.students.append(student_id)
        self.updated_at = datetime.utcnow()

    def remove_student(self, student_id: ObjectId):
        if student_id not in self.students:
            raise ClassUpdateException(str(self.id), "remove student", "Student not found")
        self.students.remove(student_id)
        self.updated_at = datetime.utcnow()

    def assign_teacher(self, teacher_id: Optional[ObjectId]):
        if self.homeroom_teacher == teacher_id:
            raise ClassUpdateException(str(self.id), "assign teacher", "Teacher already assigned or same as before")
        self.homeroom_teacher = teacher_id
        self.updated_at = datetime.utcnow()

    def change_classroom(self, class_room: str):
        if self.class_room == class_room:
            raise ClassUpdateException(str(self.id), "change classroom", "Classroom is already set to this value")
        self.class_room = class_room
        self.updated_at = datetime.utcnow()

    def mark_deleted(self):
        self.deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def update_info(self, name: Optional[str] = None, grade: Optional[int] = None, max_students: Optional[int] = None,class_room: Optional[str] = None, status: Optional[bool] = None, academic_year: Optional[str] = None):
        updated_fields = []
        if name and name != self.name:
            self.name = name
            updated_fields.append("name")
        if grade and grade != self.grade:
            self.grade = grade
            updated_fields.append("grade")
        if max_students and max_students != self.max_students:
            # Safety: cannot set less than current enrolled
            if len(self.students) > max_students:
                raise ClassUpdateException(
                    str(self.id), "update_info", "Cannot reduce max_students below current student count"
                )
            self.max_students = max_students
            updated_fields.append("max_students")
        if class_room and class_room != self.class_room:
            self.class_room = class_room
            updated_fields.append("class_room")
        if status is not None and status != self.status:
            self.status = bool(status)
            updated_fields.append("status")
        if academic_year and academic_year != self.academic_year:
            self.academic_year = academic_year
            updated_fields.append("academic_year")
        if updated_fields:
            self.updated_at = datetime.utcnow()
        else:
            raise ClassUpdateException(str(self.id), "update_info", "No changes detected")
# -------------------------
# Factory
# -------------------------
class SchoolClassFactory:
    @classmethod
    def create_from_payload(
        cls, 
        payload: SchoolClassCreateSchema
    ) -> SchoolClass:
        homeroom_teacher = getattr(payload, "homeroom_teacher", None)
        if homeroom_teacher and not isinstance(homeroom_teacher, ObjectId):
            homeroom_teacher = ObjectId(homeroom_teacher)
        created_by = getattr(payload, "created_by", None)
        if created_by and not isinstance(created_by, ObjectId):
            created_by = ObjectId(created_by)
        students: List[ObjectId] = [s if isinstance(s, ObjectId) else ObjectId(s) for s in getattr(payload, "students", []) or []]

        return SchoolClass(
            name=payload.name,
            grade=payload.grade,
            max_students=payload.max_students,
            status=getattr(payload, "status", False),
            class_room=payload.class_room,
            homeroom_teacher=homeroom_teacher,
            students=students,
            created_by=created_by,
            created_at=getattr(payload, "created_at", None) or datetime.utcnow(),
            updated_at=getattr(payload, "updated_at", None) or datetime.utcnow(),
            deleted=getattr(payload, "deleted", False),
            deleted_at=getattr(payload, "deleted_at", None),
        )
# -------------------------
# Mapper
# -------------------------
class SchoolClassMapper:

    @classmethod
    def to_domain(cls, data: dict) -> SchoolClass:
        id_value = data.get("_id") or data.get("id")
        if id_value and not isinstance(id_value, ObjectId):
            id_value = ObjectId(id_value)


        homeroom_teacher = data.get("homeroom_teacher")
        if homeroom_teacher and not isinstance(homeroom_teacher, ObjectId):
            homeroom_teacher = ObjectId(homeroom_teacher)

        return SchoolClass(
            id=id_value,
            name=data["name"],
            grade=data["grade"],
            max_students=data["max_students"],
            status=data["status"],
            homeroom_teacher=homeroom_teacher,
            students=list(data.get("students") or []),
            class_room=data.get("class_room"),
            created_by=data.get("created_by"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            deleted=data.get("deleted", False),
            deleted_at=data.get("deleted_at")
        )

    @staticmethod
    def to_safe_dict(domain: SchoolClass) -> dict:
        return {
            "id": str(domain.id) if domain.id else None,
            "name": domain.name,
            "grade": domain.grade,
            "max_students": domain.max_students,
            "status": domain.status,
            "homeroom_teacher": str(domain.homeroom_teacher) if domain.homeroom_teacher else None,
            "students": [str(s) for s in domain.students],
            "class_room": domain.class_room,
            "deleted": domain.deleted,
            "created_by": str(domain.created_by) if domain.created_by else None,
            "created_at": domain.created_at,
            "updated_at": domain.updated_at,
            "deleted_at": domain.deleted_at
        }

    @staticmethod
    def to_persistence_dict(domain: SchoolClass) -> dict:
        return {
            "_id": domain.id or ObjectId(),
            "name": domain.name,
            "grade": domain.grade,
            "max_students": domain.max_students,
            "status": domain.status,
            "homeroom_teacher": domain.homeroom_teacher,
            "students": domain.students,
            "class_room": domain.class_room,
            "deleted": domain.deleted,
            "created_by": domain.created_by,
            "created_at": domain.created_at,
            "updated_at": domain.updated_at,
            "deleted_at": domain.deleted_at
        }

    @staticmethod
    def to_dto(domain: SchoolClass) -> SchoolClassBaseDataDTO:
        return SchoolClassBaseDataDTO(
            id=str(domain.id) if domain.id else None,
            name=domain.name,
            grade=domain.grade,
            max_students=domain.max_students,
            status=domain.status,
            homeroom_teacher=str(domain.homeroom_teacher) if domain.homeroom_teacher else None,
            students=[str(s) for s in domain.students],
            class_room=domain.class_room,
            deleted=domain.deleted,
            created_by=str(domain.created_by) if domain.created_by else None,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            deleted_at=domain.deleted_at
        )
        