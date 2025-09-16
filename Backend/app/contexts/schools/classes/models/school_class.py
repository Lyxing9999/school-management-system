from datetime import datetime
from typing import List
from bson import ObjectId
from app.contexts.schools.classes.data_transfer.requests import ClassCreateRequestSchema
from app.contexts.schools.classes.error.school_exceptions import ClassFullException


# -------------------------
# Domain Model
# -------------------------
class SchoolClass:
    def __init__(
        self,
        name: str,
        grade: int,
        owner_id: ObjectId,
        max_students: int,
        status: bool,
        created_by: ObjectId,
        id: ObjectId | None = None,
        homeroom_teacher: ObjectId | None = None,
        subjects: List[str] | None = None,
        students: List[str] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        deleted: bool = False,
        deleted_at: datetime | None = None
    ):
        self.id = id
        self.name = name
        self.grade = grade
        self.owner_id = owner_id
        self.max_students = max_students
        self.status = status
        self.created_by = created_by
        self.homeroom_teacher = homeroom_teacher
        self.subjects = subjects or []
        self.students = students or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted = deleted
        self.deleted_at = deleted_at

    # -------------------------
    # Business Logic Methods
    # -------------------------
    def is_full(self) -> bool:
        return len(self.students) >= self.max_students

    def add_student(self, student_id: str):
        if self.is_full():
            raise ClassFullException(self.max_students)
        if student_id not in self.students:
            self.students.append(student_id)
            self.updated_at = datetime.utcnow()

    def remove_student(self, student_id: str):
        if student_id in self.students:
            self.students.remove(student_id)
            self.updated_at = datetime.utcnow()

    def assign_teacher(self, teacher_id: str):
        if self.homeroom_teacher != teacher_id:
            self.homeroom_teacher = teacher_id
            self.updated_at = datetime.utcnow()

    def add_subject(self, subject: str):
        if subject not in self.subjects:
            self.subjects.append(subject)
            self.updated_at = datetime.utcnow()

    def add_subjects(self, subjects: List[str]):
        added = False
        for subject in subjects:
            if subject not in self.subjects:
                self.subjects.append(subject)
                added = True
        if added:
            self.updated_at = datetime.utcnow()

    def mark_deleted(self):
        self.deleted = True
        self.deleted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()


# -------------------------
# Factory
# -------------------------
class SchoolClassFactory:
    @classmethod
    def create_from_payload(
        cls, 
        payload: ClassCreateRequestSchema, 
        owner_id: ObjectId, 
        created_by: ObjectId
    ) -> SchoolClass:
        homeroom_teacher = getattr(payload, "homeroom_teacher", None)
        if homeroom_teacher and not isinstance(homeroom_teacher, ObjectId):
            homeroom_teacher = ObjectId(homeroom_teacher)

        subjects: List[str] = [str(s) for s in getattr(payload, "subjects", []) or []]
        students: List[str] = [str(s) for s in getattr(payload, "students", []) or []]

        return SchoolClass(
            name=payload.name,
            grade=payload.grade,
            owner_id=owner_id,
            max_students=payload.max_students,
            status=getattr(payload, "status", False),
            created_by=created_by,
            homeroom_teacher=homeroom_teacher,
            subjects=subjects,
            students=students,
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

        owner_id = data.get("owner_id")
        if owner_id and not isinstance(owner_id, ObjectId):
            owner_id = ObjectId(owner_id)

        homeroom_teacher = data.get("homeroom_teacher")
        if homeroom_teacher and not isinstance(homeroom_teacher, ObjectId):
            homeroom_teacher = ObjectId(homeroom_teacher)

        return SchoolClass(
            id=id_value,
            name=data["name"],
            grade=data["grade"],
            owner_id=owner_id,
            max_students=data["max_students"],
            status=data["status"],
            homeroom_teacher=homeroom_teacher,
            subjects=list(data.get("subjects") or []),
            students=list(data.get("students") or []),
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
            "owner_id": str(domain.owner_id) if domain.owner_id else None,
            "max_students": domain.max_students,
            "status": domain.status,
            "homeroom_teacher": str(domain.homeroom_teacher) if domain.homeroom_teacher else None,
            "subjects": [str(s) for s in domain.subjects],
            "students": [str(s) for s in domain.students],
            "deleted": domain.deleted,
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
            "owner_id": domain.owner_id,
            "max_students": domain.max_students,
            "status": domain.status,
            "created_by": domain.created_by,
            "homeroom_teacher": domain.homeroom_teacher,
            "subjects": domain.subjects,
            "students": domain.students,
            "deleted": domain.deleted,
            "created_at": domain.created_at,
            "updated_at": domain.updated_at,
            "deleted_at": domain.deleted_at
        }