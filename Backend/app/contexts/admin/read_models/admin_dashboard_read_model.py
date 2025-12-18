# app/contexts/admin/read_models/admin_dashboard_read_model.py

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from zoneinfo import ZoneInfo
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.error.mongo_error_mixin import MongoErrorMixin
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.student.read_models.student_read_model import StudentReadModel
from app.contexts.shared.services.display_name_service import DisplayNameService
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.staff.read_model import StaffReadModel


class AdminDashboardReadModel(MongoErrorMixin):
    def __init__(self, db: Database) -> None:
        self._attendance = AttendanceReadModel(db)
        self._classes = ClassReadModel(db)
        self._student = StudentReadModel(db)
        self._subject = SubjectReadModel(db)
        self._grade = GradeReadModel(db)
        self._schedule = ScheduleReadModel(db)
        self._iam = IAMReadModel(db)
        self._staff = StaffReadModel(db)

        self._display_names = DisplayNameService(
            iam_read_model=self._iam,
            staff_read_model=self._staff,
            class_read_model=self._classes,
            subject_read_model=self._subject,
            student_read_model=self._student,
        )

    # --------------- OVERVIEW ---------------

    def get_overview_counters(self) -> Dict[str, int]:
        """
        Simple counters for the top cards on the admin dashboard.
        """
        tz = ZoneInfo("Asia/Phnom_Penh")
        today = datetime.now(tz).date()

        return {
            "total_students": self._student.count_active_students(),
            "total_teachers": self._staff.count_active_teachers(),
            "total_classes": self._classes.count_active_classes(),
            "total_subjects": self._subject.count_active_subjects(),
            "today_lessons": self._schedule.count_lessons_for_date(today),
        }

    # --------------- ATTENDANCE ---------------

    def get_attendance_dashboard(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> Dict[str, Any]:
        """
        Admin attendance dashboard payload:

        {
        "status_summary": [...],
        "daily_trend": [...],
        "by_class": [...],
        "top_absent_students": [...]
        }
        """
        # --- Status summary (present/absent/excused totals) ---
        status_summary = self._attendance.aggregate_status_summary(
            date_from=date_from,
            date_to=date_to,
            class_id=None,
        )

        # --- Daily trend; ensure we add "total" field ---
        daily_raw = self._attendance.aggregate_daily_status_counts(
            date_from=date_from,
            date_to=date_to,
            class_id=None,
        )

        daily_trend: List[Dict[str, Any]] = []
        for row in daily_raw:
            present = int(row.get("present", 0))
            absent = int(row.get("absent", 0))
            excused = int(row.get("excused", 0))
            total = present + absent + excused

            daily_trend.append(
                {
                    "date": row.get("date"),
                    "present": present,
                    "absent": absent,
                    "excused": excused,
                    "total": total,
                }
            )

        # --- By class; add class_name ---
        by_class_raw = self._attendance.aggregate_status_by_class(
            date_from=date_from,
            date_to=date_to,
        )
        class_ids = [ObjectId(row["class_id"]) for row in by_class_raw]
        class_name_map = self._display_names.class_names_for_ids(class_ids)
 

        by_class: List[Dict[str, Any]] = []
        for row in by_class_raw:
            cid_str = row["class_id"]
            cid = ObjectId(cid_str)

            present = int(row.get("present", 0))
            absent = int(row.get("absent", 0))
            excused = int(row.get("excused", 0))
            total = present + absent + excused

            by_class.append(
                {
                    "class_id": cid_str,
                    "class_name": class_name_map.get(cid, "Unknown"),
                    "present": present,
                    "absent": absent,
                    "excused": excused,
                    "total": total,
                }
            )

        # --- Top absent students; now with class_id + class_name ---
        top_absent_raw = self._attendance.aggregate_top_absent_students(
            limit=10,
            date_from=date_from,
            date_to=date_to,
            class_id=None,
        )

        # collect class_ids from that aggregation
        top_class_ids: list[ObjectId] = []
        for row in top_absent_raw:
            cid_str = row.get("class_id")
            if cid_str:
                try:
                    top_class_ids.append(ObjectId(cid_str))
                except Exception:
                    pass

        top_class_name_map: dict[ObjectId, str] = {}
        if top_class_ids:
            top_class_name_map = self._display_names.class_names_for_ids(
                top_class_ids
            )

        student_ids = [ObjectId(row["student_id"]) for row in top_absent_raw]
        student_name_map = self._display_names.student_names_for_student_ids(student_ids)

        top_absent_students: List[Dict[str, Any]] = []
        for row in top_absent_raw:
            sid_str = row["student_id"]
            sid = ObjectId(sid_str)

            cid_str = row.get("class_id")
            cid_obj = ObjectId(cid_str) if cid_str else None

            absent_count = int(row.get("absent_count", 0))
            total_records = row.get("total_records")
            if total_records is None:
                total_records = absent_count  # fallback

            top_absent_students.append(
                {
                    "student_id": sid_str,
                    "student_name": student_name_map.get(sid, "Unknown"),
                    "class_id": cid_str,
                    "class_name": top_class_name_map.get(cid_obj, "Unknown")
                    if cid_obj
                    else None,
                    "absent_count": absent_count,
                    "total_records": total_records,
                }
            )

        return {
            "status_summary": status_summary,
            "daily_trend": daily_trend,
            "by_class": by_class,
            "top_absent_students": top_absent_students,
        }
    # --------------- GRADES ---------------

    def get_grade_dashboard(
        self,
        term: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> Dict[str, Any]:
        """
        {
          "avg_score_by_subject": [...],
          "grade_distribution": [...],
          "pass_rate_by_class": [...],
        }
        """
        # --- Average score by subject ---
        by_subject_raw = self._grade.aggregate_avg_score_by_subject(
            term=term,
            date_from=date_from,
            date_to=date_to,
        )

        subject_ids = [ObjectId(row["subject_id"]) for row in by_subject_raw]
        subject_name_map = self._display_names.subject_labels_for_ids(subject_ids)

        avg_score_by_subject: List[Dict[str, Any]] = []
        for row in by_subject_raw:
            sid_str = row["subject_id"]
            sid = ObjectId(sid_str)
            avg_score_by_subject.append(
                {
                    "subject_id": sid_str,
                    "subject_name": subject_name_map.get(sid, "Unknown"),
                    "avg_score": float(row.get("avg_score", 0.0)),
                    "sample_size": int(row.get("sample_size", 0)),
                }
            )

        # --- Grade distribution (already in {range, count} format) ---
        grade_distribution = self._grade.aggregate_grade_distribution(
            term=term,
            date_from=date_from,
            date_to=date_to,
        )

        # --- Pass rate by class; enrich with class_name, total_students ---
        pass_rate_raw = self._grade.aggregate_pass_rate_by_class(
            term=term,
            date_from=date_from,
            date_to=date_to,
        )

        class_ids = [ObjectId(row["class_id"]) for row in pass_rate_raw]
        class_name_map = self._display_names.class_names_for_ids(class_ids)

        pass_rate_by_class: List[Dict[str, Any]] = []
        for row in pass_rate_raw:
            cid_str = row["class_id"]
            cid = ObjectId(cid_str)

            total = int(row.get("total", 0))
            passed = int(row.get("passed", 0))
            avg_score = float(row.get("avg_score", 0.0))
            pass_rate = float(row.get("pass_rate", 0.0))

            pass_rate_by_class.append(
                {
                    "class_id": cid_str,
                    "class_name": class_name_map.get(cid, "Unknown"),
                    "avg_score": avg_score,
                    "pass_rate": pass_rate,
                    "total_students": total,
                    "passed": passed,
                }
            )

        return {
            "avg_score_by_subject": avg_score_by_subject,
            "grade_distribution": grade_distribution,
            "pass_rate_by_class": pass_rate_by_class,
        }

    # --------------- SCHEDULE ---------------

    def get_schedule_dashboard(self) -> Dict[str, Any]:
        """
        {
          "lessons_by_weekday": [...],
          "lessons_by_teacher": [...],
        }
        """
        weekday_raw = self._schedule.aggregate_lessons_by_weekday()
        teacher_raw = self._schedule.aggregate_lessons_by_teacher(limit=10)

        weekday_label = {
            1: "Mon",
            2: "Tue",
            3: "Wed",
            4: "Thu",
            5: "Fri",
            6: "Sat",
            7: "Sun",
        }

        # --- Lessons by weekday ---
        lessons_by_weekday: List[Dict[str, Any]] = []
        for row in weekday_raw:
            day = int(row.get("day_of_week"))
            lessons = int(row.get("lesson_count", row.get("lessons", 0)))
            lessons_by_weekday.append(
                {
                    "day_of_week": day,
                    "label": weekday_label.get(day, str(day)),
                    "lessons": lessons,
                }
            )

        # --- Lessons by teacher ---
        teacher_ids = [row["teacher_id"] for row in teacher_raw if row.get("teacher_id")]
        teacher_name_map = self._display_names.staff_names_for_ids(teacher_ids)
        teacher_name_map_str = {str(k): v for k, v in teacher_name_map.items()}

        lessons_by_teacher: List[Dict[str, Any]] = []
        for row in teacher_raw:
            tid_str = row.get("teacher_id", "")

            teacher_name = teacher_name_map_str.get(tid_str, "Unknown")
            lessons = int(row.get("lesson_count", row.get("lessons", 0)))
            classes = int(row.get("class_count", row.get("classes", 0)))

            lessons_by_teacher.append(
                {
                    "teacher_id": tid_str,
                    "teacher_name": teacher_name,
                    "lessons": lessons,
                    "classes": classes,
                }
            )

        return {
            "lessons_by_weekday": lessons_by_weekday,
            "lessons_by_teacher": lessons_by_teacher,
        }

    # --------------- COMBINED ---------------

    def get_admin_dashboard(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        term: str | None = None,
    ) -> Dict[str, Any]:
        overview = self.get_overview_counters()
        attendance = self.get_attendance_dashboard(date_from, date_to)
        grades = self.get_grade_dashboard(term, date_from, date_to)
        schedule = self.get_schedule_dashboard()

        return {
            "overview": overview,
            "attendance": attendance,
            "grades": grades,
            "schedule": schedule,
        }