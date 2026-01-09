from __future__ import annotations

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

from app.contexts.notifications.services.notification_service import NotificationService
from app.contexts.notifications.utils.recipient_resolver import NotificationRecipientResolver
from app.contexts.notifications.types import NotifType


class TeacherService:
    def __init__(self, db: Database):
        self.school_service = SchoolService(db)
        self._teacher_read = TeacherReadModel(db)


        self.notification_service = NotificationService(db)
        self.notif_resolver = NotificationRecipientResolver(db)

    @property
    def teacher_read(self) -> TeacherReadModel:
        return self._teacher_read

    def _oid(self, v: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(v)

    # -------------------------------------------------
    # Permission helpers
    # -------------------------------------------------

    def _assert_homeroom(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
    ) -> None:
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)
        if not self.teacher_read.is_homeroom_teacher(teacher_id=tid, class_id=cid):
            raise TeacherForbiddenException()

    def _assert_can_view_class_roster(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
    ) -> None:
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)

        if self.teacher_read.is_homeroom_teacher(teacher_id=tid, class_id=cid):
            return
        if self.teacher_read.has_any_assignment_in_class(teacher_id=tid, class_id=cid):
            return

        raise TeacherForbiddenException()

    def _assert_subject_teacher(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        subject_id: Union[str, ObjectId],
    ) -> None:
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)
        sid = self._oid(subject_id)

        if not self.teacher_read.is_assigned_subject_teacher(
            teacher_id=tid,
            class_id=cid,
            subject_id=sid,
        ):
            raise TeacherForbiddenException()

    def _assert_grade_permission_from_doc(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        grade_doc: dict,
    ) -> None:
        tid = self._oid(teacher_id)

        # 1) Owner always has permission
        owner = grade_doc.get("teacher_id")
        if owner and str(owner) == str(tid):
            return

        # 2) Co-teacher: assigned to same subject in class
        cid = grade_doc.get("class_id")
        sid = grade_doc.get("subject_id")
        if cid and sid and self.teacher_read.is_assigned_subject_teacher(
            teacher_id=tid,
            class_id=cid,
            subject_id=sid,
        ):
            return

        raise TeacherForbiddenException()

    # -------------------------------------------------
    # Notifications (Grades -> Student)
    # -------------------------------------------------

    def _notify_student_grade_published(
        self,
        *,
        student_id: Union[str, ObjectId],
        grade_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId] | None = None,
        subject_id: Union[str, ObjectId] | None = None,
        term: str | None = None,
        grade_type: str | None = None,
        score: Any | None = None,
        title: str | None = None,
        message: str | None = None,
    ) -> None:
        """
        Best-effort notification to student when grade is created/updated.

        - Uses your existing resolver: student_id -> IAM user_id
        - Does NOT require `route` (optional). Keep data payload rich so UI can
          add routing later without changing backend.
        """
        try:
            sid = str(student_id)
            student_user_id = self.notif_resolver.student_to_user_id(sid)
            if not student_user_id:
                return

            payload: Dict[str, Any] = {
                "student_id": sid,
                "grade_id": str(grade_id),
                "class_id": str(class_id) if class_id else None,
                "subject_id": str(subject_id) if subject_id else None,
                "term": term,
                "grade_type": grade_type,
                "score": score,
                # "route": "/student/grades",  # enable later
            }
            # remove None values
            payload = {k: v for k, v in payload.items() if v is not None}

            self.notification_service.create_for_user(
                user_id=str(student_user_id),
                role="student",
                type=NotifType.GRADE_PUBLISHED,
                title=title or "Grade published",
                message=message or "A new grade has been posted to your account.",
                entity_type="grade",
                entity_id=str(grade_id),
                data=payload,
            )
        except Exception:
            # Never block grade operations due to notification failures
            return

    # -------------------------------------------------
    # Classes
    # -------------------------------------------------

    def list_my_classes_enriched(self, teacher_id: Union[str, ObjectId]) -> list[dict]:
        return self.teacher_read.list_my_classes_with_roles_enriched(self._oid(teacher_id))

    def list_my_classes_with_summary(self, teacher_id: Union[str, ObjectId]) -> Tuple[List[Dict], Dict]:
        return self.teacher_read.list_teacher_classes_with_summary(self._oid(teacher_id))

    def list_my_students_in_class(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
    ) -> list[dict]:
        self._assert_can_view_class_roster(teacher_id=teacher_id, class_id=class_id)
        return self.teacher_read.list_my_students_in_class(self._oid(class_id))

    # -------------------------------------------------
    # Attendance
    # -------------------------------------------------

    def mark_attendance(self, teacher_id: Union[str, ObjectId], payload: TeacherMarkAttendanceRequest) -> AttendanceDTO:
        self._assert_subject_teacher(
            teacher_id=teacher_id,
            class_id=payload.class_id,
            subject_id=payload.subject_id,
        )
        record = self.school_service.mark_attendance_session(
            student_id=payload.student_id,
            class_id=payload.class_id,
            subject_id=payload.subject_id,
            schedule_slot_id=payload.schedule_slot_id,
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

        class_id = doc.get("class_id")
        subject_id = doc.get("subject_id")

        if class_id and subject_id:
            try:
                self._assert_subject_teacher(teacher_id=teacher_id, class_id=class_id, subject_id=subject_id)
            except TeacherForbiddenException:
                self._assert_homeroom(teacher_id=teacher_id, class_id=class_id)

        record = self.school_service.change_attendance_status(
            attendance_id=attendance_id,
            new_status=payload.new_status,
            actor_teacher_id=teacher_id,
        )
        return attendance_to_dto(record) if record else None

    def list_attendance_for_class_enriched(
        self,
        teacher_id: str | ObjectId,
        class_id: str | ObjectId,
        *,
        record_date: str | None = None,
        subject_id: str | None = None,
        schedule_slot_id: str | None = None,
    ) -> list[dict]:
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)

        # 1) homeroom teacher => see all
        if self.teacher_read.is_homeroom_teacher(teacher_id=tid, class_id=cid):
            return self.teacher_read.list_attendance_for_class_enriched(
                class_id=cid,
                record_date=record_date,
                subject_id=self._oid(subject_id) if subject_id else None,
                schedule_slot_id=self._oid(schedule_slot_id) if schedule_slot_id else None,
                show_deleted="active",
            )

        # 2) non-homeroom => must have assignments in this class
        assigned_subject_ids: List[ObjectId] = (
            self.teacher_read.assignment_read.list_subject_ids_for_teacher_in_class(
                teacher_id=tid,
                class_id=cid,
                show_deleted="active",
            )
            or []
        )
        if not assigned_subject_ids:
            raise TeacherForbiddenException()

        assigned_set = {str(x) for x in assigned_subject_ids}

        # 2a) if subject_id provided => must be one of assigned
        if subject_id and subject_id.strip():
            sid = self._oid(subject_id)
            if str(sid) not in assigned_set:
                raise TeacherForbiddenException()

            return self.teacher_read.list_attendance_for_class_enriched(
                class_id=cid,
                record_date=record_date,
                subject_id=sid,
                schedule_slot_id=self._oid(schedule_slot_id) if schedule_slot_id else None,
                show_deleted="active",
            )

        # 2b) otherwise => show all assigned subjects
        return self.teacher_read.list_attendance_for_class_enriched(
            class_id=cid,
            record_date=record_date,
            subject_ids=assigned_subject_ids,
            schedule_slot_id=self._oid(schedule_slot_id) if schedule_slot_id else None,
            show_deleted="active",
        )

    def soft_delete_attendance(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        attendance_id: Union[str, ObjectId],
    ) -> int:
        aid = self._oid(attendance_id)
        doc = self.teacher_read.get_attendance_by_id(aid)
        if not doc:
            return 0

        class_id = doc.get("class_id")
        subject_id = doc.get("subject_id")

        if class_id and subject_id:
            try:
                self._assert_subject_teacher(teacher_id=teacher_id, class_id=class_id, subject_id=subject_id)
            except TeacherForbiddenException:
                self._assert_homeroom(teacher_id=teacher_id, class_id=class_id)

        tid = self._oid(teacher_id)
        return int(self.school_service.soft_delete_attendance(attendance_id=aid, actor_teacher_id=tid) or 0)

    def restore_attendance(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        attendance_id: Union[str, ObjectId],
    ) -> int:
        aid = self._oid(attendance_id)
        doc = self.teacher_read.get_attendance_by_id(aid)
        if not doc:
            return 0

        class_id = doc.get("class_id")
        subject_id = doc.get("subject_id")

        if class_id and subject_id:
            try:
                self._assert_subject_teacher(teacher_id=teacher_id, class_id=class_id, subject_id=subject_id)
            except TeacherForbiddenException:
                self._assert_homeroom(teacher_id=teacher_id, class_id=class_id)

        tid = self._oid(teacher_id)
        return int(self.school_service.restore_attendance(attendance_id=aid, actor_teacher_id=tid) or 0)

    # -------------------------------------------------
    # Grades
    # -------------------------------------------------

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

        # ✅ Notify student (best-effort)
        gid = getattr(grade, "id", None) or getattr(grade, "_id", None) or None
        if gid:
            self._notify_student_grade_published(
                student_id=payload.student_id,
                grade_id=gid,
                class_id=payload.class_id,
                subject_id=payload.subject_id,
                term=getattr(payload, "term", None),
                grade_type=getattr(payload, "type", None),
                score=getattr(payload, "score", None),
                title="Grade published",
                message="A new grade has been posted.",
            )

        return grade_to_dto(grade)

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

        grade = self.school_service.update_grade_score(
            grade_id=grade_id,
            new_score=payload.score,
            actor_teacher_id=teacher_id,
        )

        # ✅ Notify student (best-effort)
        if grade:
            self._notify_student_grade_published(
                student_id=doc.get("student_id"),
                grade_id=gid,
                class_id=doc.get("class_id"),
                subject_id=doc.get("subject_id"),
                term=doc.get("term"),
                grade_type=doc.get("type"),
                score=payload.score,
                title="Grade updated",
                message="A grade score has been updated.",
            )

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

        grade = self.school_service.change_grade_type(
            grade_id=grade_id,
            new_type=payload.type,
            actor_teacher_id=teacher_id,
        )

        if grade:
            self._notify_student_grade_published(
                student_id=doc.get("student_id"),
                grade_id=gid,
                class_id=doc.get("class_id"),
                subject_id=doc.get("subject_id"),
                term=doc.get("term"),
                grade_type=payload.type,
                score=doc.get("score"),
                title="Grade updated",
                message="A grade type has been updated.",
            )

        return grade_to_dto(grade) if grade else None

    def soft_delete_grade(self, *, teacher_id: Union[str, ObjectId], grade_id: Union[str, ObjectId]) -> int:
        gid = self._oid(grade_id)
        doc = self.teacher_read.get_grade_by_id(gid)
        if not doc:
            return 0

        self._assert_grade_permission_from_doc(teacher_id=teacher_id, grade_doc=doc)
        tid = self._oid(teacher_id)
        return int(self.school_service.soft_delete_grade(grade_id=gid, actor_teacher_id=tid) or 0)

    def restore_grade(self, *, teacher_id: Union[str, ObjectId], grade_id: Union[str, ObjectId]) -> int:
        gid = self._oid(grade_id)
        doc = self.teacher_read.get_grade_by_id(gid)
        if not doc:
            return 0

        self._assert_grade_permission_from_doc(teacher_id=teacher_id, grade_doc=doc)
        tid = self._oid(teacher_id)
        return int(self.school_service.restore_grade(grade_id=gid, actor_teacher_id=tid) or 0)

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
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)

        # 1) Check homeroom
        is_homeroom = self.teacher_read.is_homeroom_teacher(teacher_id=tid, class_id=cid)

        # 2) Assigned subjects in this class
        assigned_subject_ids: List[ObjectId] = (
            self.teacher_read.assignment_read.list_subject_ids_for_teacher_in_class(
                teacher_id=tid,
                class_id=cid,
                show_deleted="active",
            )
            or []
        )
        assigned_subject_strs = {str(s) for s in assigned_subject_ids}

        teacher_filter_id = None

        # Conservative security: if not homeroom, default to own grades unless your read model supports subject_ids list.
        if not is_homeroom:
            if subject_id:
                if str(subject_id) not in assigned_subject_strs:
                    teacher_filter_id = tid
            else:
                teacher_filter_id = tid

        # 3) Fetch
        result = self.teacher_read.list_grades_for_class_enriched_paged(
            class_id=cid,
            teacher_id=teacher_filter_id,
            subject_id=subject_id,
            page=page,
            page_size=page_size,
            term=term,
            grade_type=grade_type,
            q=q,
        )

        # 4) Decorate items
        items = result.get("items", []) or []
        for item in items:
            g_teacher_id = str(item.get("teacher_id"))
            g_subject_id = str(item.get("subject_id"))

            is_owner = (g_teacher_id == str(tid))
            is_assigned = (g_subject_id in assigned_subject_strs)

            item["can_edit"] = is_owner or is_assigned
            item["is_homeroom"] = is_homeroom

        result["is_homeroom"] = is_homeroom
        return result

    # -------------------------------------------------
    # Schedule
    # -------------------------------------------------

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
            teacher_id=self._oid(teacher_id),
            page=page,
            page_size=page_size,
            sort=sort,
            class_id=self._oid(class_id) if class_id else None,
            day_of_week=day_of_week,
            start_time_from=start_time_from,
            start_time_to=start_time_to,
        )

    def list_schedule_slot_select_for_teacher(
        self,
        *,
        teacher_id: str,
        class_id: str,
        date: str | None = None,
        day_of_week: int | None = None,
        limit: int = 200,
    ):
        return self.teacher_read.list_schedule_slot_select_for_teacher(
            teacher_id=teacher_id,
            class_id=class_id,
            date=date,
            day_of_week=day_of_week,
            limit=limit,
        )

    # -------------------------------------------------
    # Selects
    # -------------------------------------------------

    def list_class_name_options_for_teacher(self, *, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        return self.teacher_read.list_class_name_options_for_teacher_scope(self._oid(teacher_id))

    def list_student_name_options_in_class(
        self,
        *,
        class_id: Union[str, ObjectId],
        teacher_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        self._assert_can_view_class_roster(teacher_id=teacher_id, class_id=class_id)
        return self.teacher_read.list_student_name_options_in_class(self._oid(class_id))

    def list_subject_name_options_in_class(
        self,
        *,
        class_id: Union[str, ObjectId],
        teacher_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        return self.teacher_read.list_subject_name_options_in_class_for_teacher(
            class_id=self._oid(class_id),
            teacher_id=self._oid(teacher_id),
        )

    # -------------------------------------------------
    # Assignments (UI)
    # -------------------------------------------------

    def list_my_assignments_enriched(self, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        return self.teacher_read.list_my_assignments_enriched(self._oid(teacher_id))