
from typing import List, Union, Dict, Any, Tuple, Optional
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.services.legacy.school_service import SchoolService
from app.contexts.teacher.read_models.teacher_read_models import TeacherReadModel
from app.contexts.teacher.errors.teacher_exceptions import TeacherForbiddenException
from app.contexts.shared.model_converter import mongo_converter

from app.contexts.teacher.data_transfer.requests import (
    TeacherMarkAttendanceRequest,
    TeacherChangeAttendanceStatusRequest,
    TeacherAddGradeRequest,
    TeacherUpdateGradeScoreRequest,
    TeacherChangeGradeTypeRequest,
)
from app.contexts.school.data_transfer.responses import (
    attendance_to_dto,
    grade_to_dto,
    AttendanceDTO,
    GradeDTO,
)

class TeacherService:
    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        self._teacher_read = TeacherReadModel(db)

    @property
    def teacher_read(self) -> TeacherReadModel:
        return self._teacher_read

    def _oid(self, v: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(v)

    # -------------------------
    # Permission helpers
    # -------------------------
    def _assert_homeroom(self, *, teacher_id: Union[str, ObjectId], class_id: Union[str, ObjectId]) -> None:
        if not self.teacher_read.is_homeroom_teacher(teacher_id=teacher_id, class_id=class_id):
            raise TeacherForbiddenException()
    def _assert_can_view_class_roster(self, *, teacher_id, class_id) -> None:
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)

        if self.teacher_read.is_homeroom_teacher(teacher_id=tid, class_id=cid):
            return

        if self.teacher_read.has_any_assignment_in_class(teacher_id=tid, filters={"class_id": cid}):
            return

        raise TeacherForbiddenException()

    def _assert_subject_teacher(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        subject_id: Union[str, ObjectId],
    ) -> None:
        if not self.teacher_read.is_assigned_subject_teacher(
            teacher_id=teacher_id,
            class_id=class_id,
            subject_id=subject_id,
        ):
            raise TeacherForbiddenException()

    # -------------------------
    # Classes
    # -------------------------
    def list_my_classes_enriched(self, teacher_id: Union[str, ObjectId]) -> list[dict]:
        # Recommended: include both homeroom and teaching-assignment classes
        return self.teacher_read.list_my_classes_with_roles_enriched(teacher_id)

    def list_my_classes_with_summary(self, teacher_id: Union[str, ObjectId]) -> Tuple[List[Dict], Dict]:
        oid = self._oid(teacher_id)
        return self.teacher_read.list_teacher_classes_with_summary(oid)

    def list_my_students_in_class(self, *, teacher_id, class_id) -> list[dict]:
        self._assert_can_view_class_roster(teacher_id=teacher_id, class_id=class_id)
        return self.teacher_read.list_my_students_in_class(class_id)
    # -------------------------
    # Attendance (homeroom-only MVP)
    # -------------------------
    def mark_attendance(self, teacher_id: Union[str, ObjectId], payload: TeacherMarkAttendanceRequest) -> AttendanceDTO:
        self._assert_homeroom(teacher_id=teacher_id, class_id=payload.class_id)
        record = self.school_service.mark_attendance(
            student_id=payload.student_id,
            class_id=payload.class_id,
            status=payload.status,
            teacher_id=teacher_id,
            record_date=payload.record_date,
        )
        return attendance_to_dto(record)

    def change_attendance_status(
        self,
        teacher_id: Union[str, ObjectId],
        attendance_id: Union[str, ObjectId],
        payload: TeacherChangeAttendanceStatusRequest,
    ) -> Optional[AttendanceDTO]:
        aid = self._oid(attendance_id)
        doc = self.teacher_read.get_attendance_by_id(aid)
        if not doc:
            return None

        self._assert_homeroom(teacher_id=teacher_id, class_id=doc.get("class_id"))

        record = self.school_service.change_attendance_status(
            attendance_id=attendance_id,
            new_status=payload.new_status,
        )
        return attendance_to_dto(record) if record else None

    def list_attendance_for_class_enriched(
        self,
        teacher_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        *,
        record_date: str | None = None,
    ) -> list[dict]:
        self._assert_homeroom(teacher_id=teacher_id, class_id=class_id)
        return self.teacher_read.list_attendance_for_class_enriched(
            class_id=class_id,
            record_date=record_date,
        )

    def soft_delete_attendance(self, *, teacher_id: Union[str, ObjectId], attendance_id: Union[str, ObjectId]) -> int:
        aid = self._oid(attendance_id)
        doc = self.teacher_read.get_attendance_by_id(aid)
        if not doc:
            return 0
        self._assert_homeroom(teacher_id=teacher_id, class_id=doc.get("class_id"))
        tid = self._oid(teacher_id)
        return int(self.school_service.soft_delete_attendance(attendance_id=aid, actor_id=tid) or 0)

    def restore_attendance(self, *, teacher_id: Union[str, ObjectId], attendance_id: Union[str, ObjectId]) -> int:
        aid = self._oid(attendance_id)
        doc = self.teacher_read.get_attendance_by_id(aid)
        if not doc:
            return 0
        self._assert_homeroom(teacher_id=teacher_id, class_id=doc.get("class_id"))
        tid = self._oid(teacher_id)
        return int(self.school_service.restore_attendance(attendance_id=aid, actor_id=tid) or 0)

    # -------------------------
    # Grades (assigned subject teacher)
    # -------------------------
    def add_grade(self, teacher_id: Union[str, ObjectId], payload: TeacherAddGradeRequest) -> GradeDTO:
        self._assert_subject_teacher(
            teacher_id=teacher_id,
            class_id=payload.class_id,
            subject_id=payload.subject_id,
        )
        grade = self.school_service.add_grade(
            student_id=payload.student_id,
            subject_id=payload.subject_id,
            score=payload.score,
            type=payload.type,
            teacher_id=teacher_id,
            class_id=payload.class_id,
            term=payload.term,
        )
        return grade_to_dto(grade)

    def _assert_grade_permission_from_doc(self, *, teacher_id: Union[str, ObjectId], grade_doc: dict) -> None:
        tid = self._oid(teacher_id)
        cid = grade_doc.get("class_id")
        sid = grade_doc.get("subject_id")

        # Preferred rule: permission from assignment
        if cid and sid and self.teacher_read.is_assigned_subject_teacher(teacher_id=tid, class_id=cid, subject_id=sid):
            return

        # Legacy fallback: grade.teacher_id is owner
        owner = grade_doc.get("teacher_id")
        if owner and str(owner) == str(tid):
            return

        raise TeacherForbiddenException()

    def update_grade_score(
        self,
        teacher_id: Union[str, ObjectId],
        grade_id: Union[str, ObjectId],
        payload: TeacherUpdateGradeScoreRequest,
    ) -> Optional[GradeDTO]:
        gid = self._oid(grade_id)
        doc = self.teacher_read.get_grade_by_id(gid)
        if not doc:
            return None
        self._assert_grade_permission_from_doc(teacher_id=teacher_id, grade_doc=doc)

        grade = self.school_service.update_grade_score(grade_id=grade_id, new_score=payload.score, actor_teacher_id=teacher_id)
        return grade_to_dto(grade) if grade else None

    def change_grade_type(
        self,
        teacher_id: Union[str, ObjectId],
        grade_id: Union[str, ObjectId],
        payload: TeacherChangeGradeTypeRequest,
    ) -> Optional[GradeDTO]:
        gid = self._oid(grade_id)
        doc = self.teacher_read.get_grade_by_id(gid)
        if not doc:
            return None
        self._assert_grade_permission_from_doc(teacher_id=teacher_id, grade_doc=doc)

        grade = self.school_service.change_grade_type(grade_id=grade_id, new_type=payload.type, actor_teacher_id=teacher_id)
        return grade_to_dto(grade) if grade else None

    def soft_delete_grade(self, *, teacher_id: Union[str, ObjectId], grade_id: Union[str, ObjectId]) -> int:
        gid = self._oid(grade_id)
        doc = self.teacher_read.get_grade_by_id(gid)
        if not doc:
            return 0
        self._assert_grade_permission_from_doc(teacher_id=teacher_id, grade_doc=doc)
        tid = self._oid(teacher_id)
        return int(self.school_service.soft_delete_grade(grade_id=gid, actor_id=tid) or 0)

    def restore_grade(self, *, teacher_id: Union[str, ObjectId], grade_id: Union[str, ObjectId]) -> int:
        gid = self._oid(grade_id)
        doc = self.teacher_read.get_grade_by_id(gid)
        if not doc:
            return 0
        self._assert_grade_permission_from_doc(teacher_id=teacher_id, grade_doc=doc)
        tid = self._oid(teacher_id)
        return int(self.school_service.restore_grade(grade_id=gid, actor_id=tid) or 0)

    def list_grades_for_class_enriched_paged(
            self,
            teacher_id: Union[str, ObjectId],
            class_id: Union[str, ObjectId],
            *,
            subject_id: Optional[Union[str, ObjectId]] = None,
            page: int = 1,
            page_size: int = 10,
            term: str | None = None,
            grade_type: str | None = None,
            q: str | None = None,
        ) -> Dict[str, Any]:

            is_homeroom = self.teacher_read.is_homeroom_teacher(
                teacher_id=teacher_id,
                class_id=class_id,
            )

            # If NOT homeroom, teacher can only see grades they created
            teacher_filter_id: Optional[Union[str, ObjectId]] = None
            if not is_homeroom:
                teacher_filter_id = teacher_id

            # If subject_id provided:
            # - homeroom can filter any subject
            # - non-homeroom must be assigned to that subject
            if subject_id and not is_homeroom:
                self._assert_subject_teacher(
                    teacher_id=teacher_id,
                    class_id=class_id,
                    subject_id=subject_id,
                )

            return self.teacher_read.list_grades_for_class_enriched_paged(
                class_id=class_id,
                teacher_id=teacher_filter_id,   
                subject_id=subject_id,
                page=page,
                page_size=page_size,
                term=term,
                grade_type=grade_type,
                q=q,
            )

    # -------------------------
    # Schedule (teacher_id scope)
    # -------------------------
    def list_my_schedule_enriched(
        self,
        teacher_id: Union[str, ObjectId],
        page: int = 1,
        page_size: int = 10,
        sort: list[tuple[str, int]] | None = None,
        class_id: Union[str, ObjectId] | None = None,
        day_of_week: int | None = None,
        start_time_from: str | None = None,
        start_time_to: str | None = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        return self.teacher_read.list_schedule_for_teacher_enriched(
            teacher_id=teacher_id,
            page=page,
            page_size=page_size,
            sort=sort,
            class_id=class_id,
            day_of_week=day_of_week,
            start_time_from=start_time_from,
            start_time_to=start_time_to,
        )

    # -------------------------
    # Selects
    # -------------------------
    def list_class_name_options_for_teacher(self, *, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        return self.teacher_read.list_class_name_options_for_teacher_scope(teacher_id)

    def list_student_name_options_in_class(self, *, class_id: Union[str, ObjectId], teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        self._assert_homeroom(teacher_id=teacher_id, class_id=class_id)
        return self.teacher_read.list_student_name_options_in_class(class_id)

    def list_subject_name_options_in_class(self, *, class_id: Union[str, ObjectId], teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        # assigned subjects only
        return self.teacher_read.list_subject_name_options_in_class_for_teacher(
            class_id=class_id,
            teacher_id=teacher_id,
        )

    # -------------------------
    # Assignments (UI)
    # -------------------------
    def list_my_assignments_enriched(self, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        return self.teacher_read.list_my_assignments_enriched(teacher_id)




    # -------------------------
    # Permission helpers
    # -------------------------
    def _assert_homeroom(self, *, teacher_id: Union[str, ObjectId], class_id: Union[str, ObjectId]) -> None:
        if not self.teacher_read.is_homeroom_teacher(teacher_id=teacher_id, class_id=class_id):
            raise TeacherForbiddenException()

    # -------------------------
    # Selects (used by selects_route.py)
    # -------------------------
    def list_class_name_options_for_teacher(self, *, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        # homeroom + teaching-assignment classes
        return self.teacher_read.list_class_name_options_for_teacher_scope(teacher_id)

    def list_student_name_options_in_class(
        self,
        *,
        class_id: Union[str, ObjectId],
        teacher_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:

        return self.teacher_read.list_student_name_options_in_class(class_id)

    def list_subject_name_options_in_class(
        self,
        *,
        class_id: Union[str, ObjectId],
        teacher_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        # IMPORTANT: assigned subjects only (for grades UI)
        return self.teacher_read.list_subject_name_options_in_class_for_teacher(
            class_id=class_id,
            teacher_id=teacher_id,
        )