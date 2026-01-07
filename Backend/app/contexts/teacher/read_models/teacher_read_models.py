from typing import Any, Dict, Final, List, Tuple, Union, Optional
from bson import ObjectId
from pymongo.database import Database

from app.contexts.core.errors.mongo_error_mixin import MongoErrorMixin
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.lifecycle.filters import not_deleted

from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
from app.contexts.student.read_models.student_read_model import StudentReadModel

from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.school.read_models.schedule_read_model import ScheduleReadModel
from app.contexts.school.read_models.attendance_read_model import AttendanceReadModel
from app.contexts.school.read_models.grade_read_model import GradeReadModel

from app.contexts.shared.services.display_name_service import DisplayNameService
from app.contexts.school.read_models.teacher_assignment_read_model import TeacherAssignmentReadModel


class TeacherReadModel(MongoErrorMixin):
    def __init__(self, db: Database) -> None:
        self.db: Final[Database] = db

        self.iam: Final[IAMReadModel] = IAMReadModel(db)
        self.staff: Final[StaffReadModel] = StaffReadModel(db)

        self.classes: Final[ClassReadModel] = ClassReadModel(db)
        self.subject: Final[SubjectReadModel] = SubjectReadModel(db)
        self.student: Final[StudentReadModel] = StudentReadModel(db)

        self.schedule: Final[ScheduleReadModel] = ScheduleReadModel(db)
        self.attendance: Final[AttendanceReadModel] = AttendanceReadModel(db)

        self.grade: Final[GradeReadModel] = GradeReadModel(
            db,
            student_read=self.student,
            subject_read=self.subject,
        )

        self.display: Final[DisplayNameService] = DisplayNameService(
            iam_read_model=self.iam,
            staff_read_model=self.staff,
            class_read_model=self.classes,
            subject_read_model=self.subject,
            student_read_model=self.student,
        )

        self.assignment_read: Final[TeacherAssignmentReadModel] = TeacherAssignmentReadModel(db)

    def _oid(self, v: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(v)

    # -------------------------
    # Permission checks
    # -------------------------
    def is_homeroom_teacher(self, *, teacher_id: Union[str, ObjectId], class_id: Union[str, ObjectId]) -> bool:
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)
        cls = self.classes.get_by_id(cid)
        if not cls:
            return False

        homeroom_id = cls.get("homeroom_teacher_id")
        legacy_id = cls.get("teacher_id")  # optional fallback

        return str(homeroom_id or legacy_id or "") == str(tid)

    def is_assigned_subject_teacher(
        self,
        *,
        teacher_id: Union[str, ObjectId],
        class_id: Union[str, ObjectId],
        subject_id: Union[str, ObjectId],
    ) -> bool:
        tid = self._oid(teacher_id)
        cid = self._oid(class_id)
        sid = self._oid(subject_id)
        doc = self.assignment_read.get_active_by_class_subject(cid, sid)
        return bool(doc and str(doc.get("teacher_id")) == str(tid))

    # -------------------------
    # Classes (roles-enriched)
    # -------------------------
    def list_my_classes_with_roles_enriched(self, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        tid = self._oid(teacher_id)

        # 1) homeroom classes (your existing method)
        homeroom_docs = self.classes.list_classes_for_teacher(tid) or []
        homeroom_ids = {c.get("_id") for c in homeroom_docs if c.get("_id")}

        # 2) teaching assignment classes
        assign_docs = self.assignment_read.list_for_teacher(tid, show_deleted="active")
        assign_class_ids = {d.get("class_id") for d in assign_docs if d.get("class_id")}

        # fetch missing classes
        extra_ids = [cid for cid in assign_class_ids if cid and cid not in homeroom_ids]
        extra_classes: List[dict] = []
        if extra_ids:
            extra_classes = self.classes.list_by_ids(list(extra_ids))  # implement list_by_ids in ClassReadModel if missing

        combined = list(homeroom_docs) + list(extra_classes)

        # enrich base class fields
        enriched = self.display.enrich_classes(combined) if combined else []

        # build assigned subjects per class for UI (chips)
        # {class_id -> [subject_id...]}
        by_class: Dict[str, List[ObjectId]] = {}
        for a in assign_docs:
            cid = a.get("class_id")
            sid = a.get("subject_id")
            if cid and sid:
                by_class.setdefault(str(cid), []).append(sid)

        # subject label maps (bulk)
        all_subject_ids: List[ObjectId] = []
        for sids in by_class.values():
            all_subject_ids.extend([x for x in sids if x])
        subject_label_map = self.display.subject_labels_for_ids(all_subject_ids)
        subject_label_map_str = {str(k): v for k, v in subject_label_map.items()}

        # attach role fields
        for c in enriched:
            cid = c.get("_id") or c.get("id")
            cid_str = str(cid) if cid else ""

            c["is_homeroom"] = cid in homeroom_ids or cid_str in {str(x) for x in homeroom_ids if x}
            sids = by_class.get(cid_str, [])

            labels: List[str] = []
            for sid in sids:
                labels.append(subject_label_map.get(sid) or subject_label_map_str.get(str(sid)) or "[deleted subject]")

            c["assigned_subject_labels"] = sorted(set([x for x in labels if x]))

        return enriched

    def list_teacher_classes_with_summary(self, teacher_id: Union[str, ObjectId]) -> Tuple[List[Dict], Dict]:
        docs, summary = self.classes.list_classes_for_teacher_with_summary(self._oid(teacher_id))
        enriched = self.display.enrich_classes(docs) if docs else []
        return enriched, summary

    # -------------------------
    # Students
    # -------------------------
    def list_my_students_in_class(self, class_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        return self.student.list_students_in_class(class_id, projection={"history": 0})

    def list_student_name_options_in_class(self, class_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        students = self.student.list_student_ids_in_class(self._oid(class_id))
        student_ids = [s for s in (students or []) if s]
        return self.display.student_select_options_for_ids(student_ids)

    # -------------------------
    # Subjects select: assigned-only
    # -------------------------
    def list_subject_name_options_in_class_for_teacher(
        self,
        *,
        class_id: Union[str, ObjectId],
        teacher_id: Union[str, ObjectId],
    ) -> List[Dict[str, Any]]:
        cid = self._oid(class_id)
        tid = self._oid(teacher_id)

        docs = self.assignment_read.list_for_teacher(tid, show_deleted="active")
        subject_ids = [
            d.get("subject_id")
            for d in docs
            if d.get("subject_id") and str(d.get("class_id")) == str(cid)
        ]
        if not subject_ids:
            return []

        label_map = self.display.subject_labels_for_ids(subject_ids)
        label_map_str = {str(k): v for k, v in label_map.items()}

        items = []
        for sid in subject_ids:
            label = label_map.get(sid) or label_map_str.get(str(sid)) or ""
            if label:
                items.append({"value": str(sid), "label": label})

        items.sort(key=lambda x: (x.get("label") or "").lower())
        return items
    # -------------------------
    # Schedule & grades enrichment
    # -------------------------
    def list_schedule_for_teacher_enriched(self, *args, **kwargs):
        items, total = self.schedule.list_schedules_for_teacher_paginated(*args, **kwargs)
        if not items:
            return [], total
        return self.display.enrich_schedules(items), total

    def get_attendance_by_id(self, att_id: ObjectId) -> dict | None:
        return self.attendance.get_by_id(att_id)

    def get_grade_by_id(self, grade_id: ObjectId) -> dict | None:
        return self.grade.get_by_id(grade_id)

    def list_grades_for_class_enriched_paged(
        self,
        *,
        class_id: Union[str, ObjectId],
        teacher_id: Optional[Union[str, ObjectId]] = None,  
        subject_id: Optional[Union[str, ObjectId]] = None,
        page: int = 1,
        page_size: int = 10,
        term: str | None = None,
        grade_type: str | None = None,
        q: str | None = None,
    ) -> Dict[str, Any]:

        result = self.grade.list_grades_for_class_paged(
            class_id=class_id,
            teacher_id=teacher_id,       
            subject_id=subject_id,
            page=page,
            page_size=page_size,
            term=term,
            grade_type=grade_type,
            q=q,
            sort="-created_at",
            show_deleted="active",
        )

        result["items"] = self.display.enrich_grades(result["items"])
        return result

    # -------------------------
    # Classes select scope
    # -------------------------
    def list_class_name_options_for_teacher_scope(self, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        # build from roles-enriched classes (homeroom + teaching)
        classes = self.list_my_classes_with_roles_enriched(teacher_id)
        out: List[Dict[str, Any]] = []
        for c in classes:
            cid = c.get("_id") or c.get("id")
            label = c.get("name") or c.get("class_name") or ""
            if cid and label:
                out.append({"value": str(cid), "label": str(label)})
        out.sort(key=lambda x: (x.get("label") or "").lower())
        return out
        

    def has_any_assignment_in_class(self, teacher_id: Union[str, ObjectId], *, filters: Dict[str, Any]) -> bool:
        q = {**filters, "teacher_id": self._oid(teacher_id)}
        return self.assignment_read.exists(q, show_deleted="active")
    # -------------------------
    # Assignments list (enriched)
    # -------------------------
    def list_my_assignments_enriched(self, teacher_id: Union[str, ObjectId]) -> List[Dict[str, Any]]:
        tid = self._oid(teacher_id)
        docs = self.assignment_read.list_for_teacher(tid, show_deleted="active")
        if not docs:
            return []

        # normalize ids for converter + UI
        normalized: List[Dict[str, Any]] = []
        for d in docs:
            x = dict(d)
            if "_id" in x and "id" not in x:
                x["id"] = str(x["_id"])
            for k in ("class_id", "subject_id", "teacher_id", "assigned_by"):
                if x.get(k) is not None:
                    x[k] = str(x[k])
            normalized.append(x)

        return self.display.enrich_teaching_assignments(normalized)



    def list_attendance_for_class_enriched(
        self,
        *,
        class_id: Union[str, ObjectId],
        record_date: str | None = None,
        show_deleted: str = "active",
    ) -> list[dict]:
        docs = self.attendance.list_attendance_for_class_by_date(
            class_id=class_id,
            record_date=record_date,
            show_deleted=show_deleted,
        )
        if not docs:
            return []
        return self.display.enrich_attendance(docs)