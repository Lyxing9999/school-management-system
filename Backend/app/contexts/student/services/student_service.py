from __future__ import annotations

from typing import Final, Optional
from bson import ObjectId
from pymongo.database import Database
from datetime import datetime

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.iam.read_models.iam_read_model import IAMReadModel

from app.contexts.student.read_models.student_read_model import StudentReadModel
from app.contexts.school.read_models.student_stats_read_model import StudentStatsReadModel

from app.contexts.student.repositories.student_repository import MongoStudentRepository
from app.contexts.student.domain.student import Student
from app.contexts.student.factory.student_factory import StudentFactory

from app.contexts.admin.data_transfer.request import AdminCreateStudentSchema, AdminUpdateStudentSchema
from app.contexts.student.errors.student_exceptions import StudentNotFoundException, StudentUserNotFoundException, StudentUpdateFailedException


class StudentService:
    """
    EN: Student write-side service + delegates read use-cases to StudentStatsReadModel.
    KH: Service សម្រាប់ Student (write side) ហើយ read use-case ទៅ StudentStatsReadModel។
    """

    def __init__(self, db: Database):
        self.db = db

        self._student_read: Final[StudentReadModel] = StudentReadModel(db)          # basic student reads
        self._student_stats: Final[StudentStatsReadModel] = StudentStatsReadModel(db)  # cross-collection UI reads

        self._iam_read: Final[IAMReadModel] = IAMReadModel(db)

        self._student_repo: Final[MongoStudentRepository] = MongoStudentRepository(db["students"])
        self._student_factory: Final[StudentFactory] = StudentFactory(self._student_read, self._iam_read)

    def _oid(self, id_: str | ObjectId) -> ObjectId:
        return mongo_converter.convert_to_object_id(id_)

    # ---------------- FINDERS (raise in service) ----------------

    def get_student_by_user_id(self, user_id: str | ObjectId) -> Student:
        user_oid = self._oid(user_id)
        student = self._student_repo.find_by_user_id(user_oid)
        if not student:
            raise StudentUserNotFoundException(user_id=user_oid)
        return student

    def get_student_by_id(self, student_id: str | ObjectId) -> Student:
        sid = self._oid(student_id)
        student = self._student_repo.find_by_id(sid)
        if not student:
            raise StudentNotFoundException(student_id=sid)
        return student

    def get_current_class_id(self, student_id: str | ObjectId) -> Optional[ObjectId]:
        student = self.get_student_by_id(student_id)
        return student.current_class_id

    # ---------------- ADMIN WRITE ----------------

    def create_student_profile(
        self,
        *,
        payload: AdminCreateStudentSchema,
        user_id: str | ObjectId,
        created_by: str | ObjectId,
    ) -> Student:
        user_oid = self._oid(user_id)
        created_by_oid = self._oid(created_by)

        dob_val = payload.dob
        if isinstance(dob_val, str):
            dob_val = datetime.strptime(dob_val, "%Y-%m-%d").date()

        student = self._student_factory.create_student(
            user_id=user_oid,
            student_id_code=payload.student_id_code,
            first_name_kh=payload.first_name_kh,
            last_name_kh=payload.last_name_kh,
            first_name_en=payload.first_name_en,
            last_name_en=payload.last_name_en,
            gender=payload.gender,
            dob=dob_val,
            current_grade_level=payload.current_grade_level,
            current_class_id=self._oid(payload.current_class_id) if payload.current_class_id else None,
            photo_url=payload.photo_url,
            phone_number=payload.phone_number,
            address=payload.address,
            guardians=payload.guardians,
            created_by=created_by_oid,
        )

        return self._student_repo.insert(student)

    def update_student_profile(
        self,
        *,
        user_id: str | ObjectId,
        payload: AdminUpdateStudentSchema,
    ) -> Student:
        user_oid = self._oid(user_id)
        student = self._student_repo.find_by_user_id(user_oid)
        if not student:
            raise StudentNotFoundException(student_id=user_oid) 
        data = payload.model_dump(exclude_unset=True)
        student.admin_update_general_info(data)
        updated = self._student_repo.update(student)

        if not updated:
            raise StudentUpdateFailedException()
        return updated

    # ---------------- CLASS MEMBERSHIP (write) ----------------

    def join_class(self, class_id: str | ObjectId, student_id: str | ObjectId) -> Student:
        cid = self._oid(class_id)
        student = self.get_student_by_id(student_id)
        student.join_class(cid)
        updated = self._student_repo.update(student)
        if not updated:
            raise StudentUpdateFailedException()
        return updated

    def leave_class(self, student_id: str | ObjectId) -> Student:
        student = self.get_student_by_id(student_id)
        student.leave_class()
        updated = self._student_repo.update(student)
        if not updated:
            raise StudentUpdateFailedException()
        return updated

    # ---------------- MY (READ via StudentStatsReadModel) ----------------

    def get_my_profile(self, user_id: str | ObjectId) -> Student:
        return self.get_student_by_user_id(user_id)

    def get_my_classes(self, student_id: str | ObjectId) -> list[dict]:
        return self._student_stats.list_my_classes_enriched(student_id)

    def get_my_schedule(self, student_id: str | ObjectId) -> list[dict]:
        return self._student_stats.list_my_schedule_enriched(student_id)

    def get_my_attendance(self, student_id: str | ObjectId, class_id: str | ObjectId | None = None) -> list[dict]:
        return self._student_stats.list_my_attendance_enriched(student_id, class_id)

    def get_my_grades(self, student_id: str | ObjectId, term: str | None = None) -> list[dict]:
        return self._student_stats.list_my_grades_enriched(student_id, term=term)