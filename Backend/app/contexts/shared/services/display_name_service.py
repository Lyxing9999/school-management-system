from __future__ import annotations
from typing import Iterable, Dict, List, Any, TypedDict, TYPE_CHECKING
from bson import ObjectId

from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.staff.read_models.staff_read_model import StaffReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel

from app.contexts.shared.model_converter import mongo_converter

if TYPE_CHECKING:
    from app.contexts.student.read_models.student_read_model import StudentReadModel
    
class StudentNamePack(TypedDict, total=False):
    en: str
    kh: str



class ScheduleSlotPack(TypedDict, total=False):
    day_of_week: int
    start_time: str
    end_time: str
    room: str

class DisplayNameService:
    """
    Shared helper for turning IDs into display labels for UI.

    It **never** talks directly to Mongo; it only uses read models.
    """

    def __init__(
        self,
        iam_read_model: IAMReadModel,
        staff_read_model: StaffReadModel,
        class_read_model: ClassReadModel,
        subject_read_model: SubjectReadModel,
        student_read_model: StudentReadModel,
    ) -> None:
        self.iam_read_model = iam_read_model
        self.staff_read_model = staff_read_model
        self.class_read_model = class_read_model
        self.subject_read_model = subject_read_model
        self.student_read_model = student_read_model


    @staticmethod
    def _pick_name(pack: Any, preferred: str = "en") -> str:
        if not pack:
            return "[deleted student]"

        if isinstance(pack, str):
            return pack

        if isinstance(pack, dict):
            return (
                (pack.get(preferred) or pack.get("en") or pack.get("kh") or "")
                .strip()
                or "[deleted student]"
            )

        # fallback for unexpected types
        return str(pack).strip() or "[deleted student]"

    # internal
    # -----------------------------



    @staticmethod
    def _normalize_ids(
        ids: Iterable[ObjectId | str | dict | None],
    ) -> list[ObjectId]:
        result: list[ObjectId] = []
        for raw in ids:
            if raw is None:
                continue

            # Handle Mongo-style export: {"$oid": "..."}
            if isinstance(raw, dict) and "$oid" in raw:
                raw = raw["$oid"]

            # mongo_converter can take str or ObjectId
            result.append(mongo_converter.convert_to_object_id(raw))
        return result

    # -----------------------------
    # USERS (username)
    # -----------------------------

    def username_for_id(self, user_id: ObjectId | str | None) -> str:
        if not user_id:
            return ""
        oid = mongo_converter.convert_to_object_id(user_id)
        user = self.iam_read_model.get_by_id(oid)
        return user.get("username", "") if user else ""

    def usernames_for_ids(
        self,
        user_ids: Iterable[ObjectId | str | dict | None],
        role: str | None = None,
    ) -> Dict[ObjectId, str]:
        oids = self._normalize_ids(user_ids)
        if not oids:
            return {}

        # IAMReadModel returns list[{"_id": ..., "username": ...}]
        docs = self.iam_read_model.list_usernames_by_ids(oids, role=role)
        mapping: Dict[ObjectId, str] = {}
        for doc in docs:
            _id = doc.get("_id")
            name = doc.get("username", "")
            if _id is not None:
                mapping[_id] = name
        return mapping


    def student_names_for_student_ids(
        self,
        student_ids: Iterable[ObjectId | str | dict | None],
    ) -> Dict[ObjectId, StudentNamePack]:
        oids = self._normalize_ids(student_ids)
        if not oids:
            return {}

        docs = self.student_read_model.list_student_names_by_ids(oids)

        mapping: Dict[ObjectId, StudentNamePack] = {}
        for doc in docs:
            _id = doc.get("_id")
            if _id is None:
                continue

            first_en = (doc.get("first_name_en") or "").strip()
            last_en = (doc.get("last_name_en") or "").strip()
            first_kh = (doc.get("first_name_kh") or "").strip()
            last_kh = (doc.get("last_name_kh") or "").strip()

            en = " ".join([p for p in [first_en, last_en] if p])
            kh = " ".join([p for p in [last_kh, first_kh] if p])

            mapping[_id] = {"en": en or "", "kh": kh or ""}

        return mapping
    # -----------------------------
    # STAFF (teachers)
    # -----------------------------

    def staff_names_for_ids(
        self,
        user_ids: Iterable[ObjectId | str | dict | None],
    ) -> Dict[ObjectId, str]:
        """
        :return: {user_id -> staff_name}
        """
        oids = self._normalize_ids(user_ids)
        if not oids:
            return {}
        return self.staff_read_model.list_names_by_ids(oids)

    # -----------------------------
    # CLASSES
    # -----------------------------

    def class_name_for_id(self, class_id: ObjectId | str | None) -> str:
        if not class_id:
            return ""
        doc = self.class_read_model.get_by_id(class_id)
        return doc.get("name", "") if doc else ""

    def class_names_for_ids(
        self,
        class_ids: Iterable[ObjectId | str | dict | None],
    ) -> Dict[ObjectId, str]:
        oids = self._normalize_ids(class_ids)
        if not oids:
            return {}
        return self.class_read_model.list_class_names_by_ids(oids)

    # -----------------------------
    # SUBJECTS (Name + Code)
    # -----------------------------

    def subject_label_for_id(self, subject_id: ObjectId | str | None) -> str:
        """
        Single helper: 'Math (MTH101)' or 'Math' or 'MTH101'.
        """
        if not subject_id:
            return ""
        doc = self.subject_read_model.get_by_id(subject_id)
        if not doc:
            return ""
        name = doc.get("name") or ""
        code = doc.get("code") or ""
        if name and code:
            return f"{name} ({code})"
        return name or code

    def subject_labels_for_ids(
        self,
        subject_ids: Iterable[ObjectId | str | dict | None],
    ) -> Dict[ObjectId, str]:
        """
        Bulk: {subject_id -> 'Name (CODE)'}
        """
        oids = self._normalize_ids(subject_ids)
        if not oids:
            return {}

        # You can implement `list_by_ids` in SubjectReadModel
        docs = self.subject_read_model.list_by_ids(oids)
        mapping: Dict[ObjectId, str] = {}

        for doc in docs:
            sid: ObjectId = doc["_id"]
            name = doc.get("name") or ""
            code = doc.get("code") or ""
            label = f"{name} ({code})" if name and code else name or code
            mapping[sid] = label

        return mapping


    # -----------------------------
    # SCHEDULE ENRICHMENT
    # -----------------------------

    def enrich_schedules(self, schedule_docs: Iterable[dict]) -> List[dict]:
        """
        Take raw schedule docs and attach:

        - class_name (or "[deleted class]")
        - teacher_name (or "[deleted teacher]")
        - subject_label (or "[deleted subject]")

        It does NOT hit Mongo directly; it uses the other helpers.
        """
        docs: List[dict] = [dict(d) for d in schedule_docs]

        class_ids: list[ObjectId | str | dict | None] = []
        teacher_ids: list[ObjectId | str | dict | None] = []
        subject_ids: list[ObjectId | str | dict | None] = []

        for d in docs:
            cid = d.get("class_id")
            tid = d.get("teacher_id")
            sid = d.get("subject_id")

            if cid is not None:
                class_ids.append(cid)
            if tid is not None:
                teacher_ids.append(tid)
            if sid is not None:
                subject_ids.append(sid)

        class_name_map = self.class_names_for_ids(class_ids)
        teacher_name_map = self.staff_names_for_ids(teacher_ids)
        subject_label_map = self.subject_labels_for_ids(subject_ids)

        # string-keyed copies (for when ids in docs are strings)
        class_name_map_str = {str(k): v for k, v in class_name_map.items()}
        teacher_name_map_str = {str(k): v for k, v in teacher_name_map.items()}
        subject_label_map_str = {str(k): v for k, v in subject_label_map.items()}

        for d in docs:
            cid = d.get("class_id")
            tid = d.get("teacher_id")
            sid = d.get("subject_id")

            if cid is not None:
                name = class_name_map.get(cid) or class_name_map_str.get(str(cid))
                d["class_name"] = name if name is not None else "[deleted class]"

            if tid is not None:
                tname = teacher_name_map.get(tid) or teacher_name_map_str.get(str(tid))
                d["teacher_name"] = tname if tname is not None else "[deleted teacher]"

            if sid is not None:
                slabel = (
                    subject_label_map.get(sid)
                    or subject_label_map_str.get(str(sid))
                )
                d["subject_label"] = slabel if slabel is not None else "[deleted subject]"

        return docs


    # -----------------------------
    # CLASS ENRICHMENT
    # -----------------------------

    def enrich_classes(self, class_docs: Iterable[dict]) -> List[dict]:
        """
        Take raw class docs and attach:

        - homeroom_teacher_id (or "[deleted teacher]")
        - subject_labels: list of "Name (CODE)" or "[deleted subject]"
        - student_count
        - subject_count
        """

        docs: List[dict] = [dict(d) for d in class_docs]

        teacher_ids: list[ObjectId | str | dict] = []
        all_subject_ids: list[ObjectId | str | dict] = []

        # Collect all IDs from the docs
        for d in docs:
            tid = d.get("homeroom_teacher_id")
            if tid is not None:
                teacher_ids.append(tid)

            sids = d.get("subject_ids") or []
            for sid in sids:
                if sid is not None:
                    all_subject_ids.append(sid)

        # Build maps using existing helpers
        teacher_name_map = self.staff_names_for_ids(teacher_ids)
        subject_label_map = self.subject_labels_for_ids(all_subject_ids)

        # Also support string keys (in case ids in docs are str)
        teacher_name_map_str = {str(k): v for k, v in teacher_name_map.items()}
        subject_label_map_str = {str(k): v for k, v in subject_label_map.items()}

        # Attach enriched fields to each class doc
        for d in docs:
            tid = d.get("homeroom_teacher_id")
            sids = d.get("subject_ids") or []
            enrollments = d.get("enrolled_count") or []

            # Teacher name
            if tid is not None:
                tname = (
                    teacher_name_map.get(tid)
                    or teacher_name_map_str.get(str(tid))
                )
                d["homeroom_teacher_name"] = (
                    tname if tname is not None else "[deleted teacher]"
                )

            # Subject labels
            labels: list[str] = []
            for sid in sids:
                slabel = (
                    subject_label_map.get(sid)
                    or subject_label_map_str.get(str(sid))
                )
                labels.append(
                    slabel if slabel is not None else "[deleted subject]"
                )
            d["subject_labels"] = labels

            # Simple counts (handy for UI)
            d["student_count"] = enrollments
            d["subject_count"] = len(sids)
        
        return docs




    # -----------------------------
    # ATTENDANCE ENRICHMENT
    # -----------------------------
    def enrich_attendance(self, attendance_docs: Iterable[dict]) -> List[dict]:
        docs: List[dict] = [dict(d) for d in attendance_docs]

        student_ids: list[ObjectId | str | dict | None] = []
        class_ids: list[ObjectId | str | dict | None] = []
        teacher_ids: list[ObjectId | str | dict | None] = []
        subject_ids: list[ObjectId | str | dict | None] = []
        slot_ids: list[ObjectId | str | dict | None] = []

        for d in docs:
            student_ids.append(d.get("student_id"))
            class_ids.append(d.get("class_id"))
            teacher_ids.append(d.get("marked_by_teacher_id"))
            subject_ids.append(d.get("subject_id"))
            slot_ids.append(d.get("schedule_slot_id"))

        student_name_map = self.student_names_for_student_ids(student_ids)
        class_name_map = self.class_names_for_ids(class_ids)
        teacher_name_map = self.staff_names_for_ids(teacher_ids)
        subject_label_map = self.subject_labels_for_ids(subject_ids)

        slot_pack_map = self.schedule_slot_packs_for_ids(slot_ids)

        # string-keyed copies (supports str ids in docs)
        student_name_map_str = {str(k): v for k, v in student_name_map.items()}
        class_name_map_str = {str(k): v for k, v in class_name_map.items()}
        teacher_name_map_str = {str(k): v for k, v in teacher_name_map.items()}
        subject_label_map_str = {str(k): v for k, v in subject_label_map.items()}
        slot_pack_map_str = {str(k): v for k, v in slot_pack_map.items()}

        for d in docs:
            sid = d.get("student_id")
            cid = d.get("class_id")
            tid = d.get("marked_by_teacher_id")
            subid = d.get("subject_id")
            slotid = d.get("schedule_slot_id")

            # student
            if sid is not None:
                pack = student_name_map.get(sid) or student_name_map_str.get(str(sid))
                d["student_name"] = self._pick_name(pack, preferred="en")

            # class
            if cid is not None:
                cname = class_name_map.get(cid) or class_name_map_str.get(str(cid))
                d["class_name"] = cname if cname is not None else "[deleted class]"

            # teacher
            if tid is not None:
                tname = teacher_name_map.get(tid) or teacher_name_map_str.get(str(tid))
                d["teacher_name"] = tname if tname is not None else "[deleted teacher]"

            # subject label
            if subid is not None:
                slabel = subject_label_map.get(subid) or subject_label_map_str.get(str(subid))
                d["subject_label"] = slabel if slabel is not None else "[deleted subject]"

            # schedule slot pack
            if slotid is not None:
                sp = slot_pack_map.get(slotid) or slot_pack_map_str.get(str(slotid))
                if sp:
                    d["day_of_week"] = sp.get("day_of_week")
                    d["start_time"] = sp.get("start_time")
                    d["end_time"] = sp.get("end_time")
                    d["room"] = sp.get("room")

        return docs


    # -----------------------------
    # GRADE ENRICHMENT
    # -----------------------------
    def enrich_grades(self, grade_docs: Iterable[dict]) -> List[dict]:
        docs: List[dict] = [dict(d) for d in grade_docs]

        student_ids = [d.get("student_id") for d in docs]
        class_ids   = [d.get("class_id") for d in docs]
        teacher_ids = [d.get("teacher_id") for d in docs]
        subject_ids = [d.get("subject_id") for d in docs]

        student_name_map = self.student_names_for_student_ids(student_ids)  
        class_name_map = self.class_names_for_ids(class_ids)
        teacher_name_map = self.staff_names_for_ids(teacher_ids)
        subject_label_map = self.subject_labels_for_ids(subject_ids)

        # string-keyed maps (for docs that have string ids)
        student_name_map_str = {str(k): v for k, v in student_name_map.items()}
        class_name_map_str = {str(k): v for k, v in class_name_map.items()}
        teacher_name_map_str = {str(k): v for k, v in teacher_name_map.items()}
        subject_label_map_str = {str(k): v for k, v in subject_label_map.items()}

        for d in docs:
            sid = d.get("student_id")
            cid = d.get("class_id")
            tid = d.get("teacher_id")
            subid = d.get("subject_id")

            # --- student ---
            if sid is not None:
                pack = student_name_map.get(sid) or student_name_map_str.get(str(sid))
                if pack:
                    d["student_name_en"] = pack.get("en") or None
                    d["student_name_kh"] = pack.get("kh") or None
                    # keep existing field for UI compatibility
                    d["student_name"] = pack.get("en") or pack.get("kh") or "[deleted student]"
                else:
                    d["student_name_en"] = None
                    d["student_name_kh"] = None
                    d["student_name"] = "[deleted student]"

            # --- class ---
            if cid is not None:
                cname = class_name_map.get(cid) or class_name_map_str.get(str(cid))
                d["class_name"] = cname if cname is not None else "[deleted class]"

            # --- teacher ---
            if tid is not None:
                tname = teacher_name_map.get(tid) or teacher_name_map_str.get(str(tid))
                d["teacher_name"] = tname if tname is not None else "[deleted teacher]"

            # --- subject ---
            if subid is not None:
                slabel = subject_label_map.get(subid) or subject_label_map_str.get(str(subid))
                d["subject_label"] = slabel if slabel is not None else "[deleted subject]"

        return docs

    # -----------------------------
    # Select Options
    # -----------------------------

    def student_select_options_for_ids(
        self,
        student_ids: Iterable[ObjectId | str | dict | None],
        *,
        include_label: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Build UI-friendly select options for students:

        [
          {
            "value": "ObjectIdString",
            "full_name_en": "...",
            "full_name_kh": "...",
            "label": "...",
          }
        ]
        """
        oids = self._normalize_ids(student_ids)
        if not oids:
            return []

        docs = self.student_read_model.list_student_names_by_ids(oids)

        options: List[Dict[str, Any]] = []
        for d in docs:
            sid = d.get("_id")
            if not sid:
                continue

            first_en = (d.get("first_name_en") or "").strip()
            last_en = (d.get("last_name_en") or "").strip()
            first_kh = (d.get("first_name_kh") or "").strip()
            last_kh = (d.get("last_name_kh") or "").strip()

            full_name_en = f"{first_en} {last_en}".strip()
            full_name_kh = f"{last_kh} {first_kh}".strip()

            label = full_name_en
            if include_label and full_name_kh:
                label = f"{full_name_en} / {full_name_kh}".strip(" /")

            options.append(
                {
                    "value": str(sid),
                    "full_name_en": full_name_en,
                    "full_name_kh": full_name_kh,
                    "label": label,
                    "first_name_en": first_en,
                    "last_name_en": last_en,
                    "first_name_kh": first_kh,
                    "last_name_kh": last_kh,
                }
            )

        options.sort(key=lambda x: (x.get("full_name_en") or x.get("label") or "").lower())
        return options


    def enrich_teaching_assignments(self, assignment_docs: Iterable[dict]) -> List[dict]:
        """
        Attach:
        - class_name
        - subject_label
        - teacher_name
        - assigned_by_username (optional, nice for audit)
        """
        docs: List[dict] = [dict(d) for d in assignment_docs]

        class_ids: list[ObjectId | str | dict | None] = []
        subject_ids: list[ObjectId | str | dict | None] = []
        teacher_ids: list[ObjectId | str | dict | None] = []
        assigned_by_ids: list[ObjectId | str | dict | None] = []

        for d in docs:
            class_ids.append(d.get("class_id"))
            subject_ids.append(d.get("subject_id"))
            teacher_ids.append(d.get("teacher_id"))
            assigned_by_ids.append(d.get("assigned_by"))

        class_name_map = self.class_names_for_ids(class_ids)
        subject_label_map = self.subject_labels_for_ids(subject_ids)
        teacher_name_map = self.staff_names_for_ids(teacher_ids)
        assigned_by_map = self.usernames_for_ids(assigned_by_ids)  # IAM usernames (optional)

        # Support string keys too
        class_name_map_str = {str(k): v for k, v in class_name_map.items()}
        subject_label_map_str = {str(k): v for k, v in subject_label_map.items()}
        teacher_name_map_str = {str(k): v for k, v in teacher_name_map.items()}
        assigned_by_map_str = {str(k): v for k, v in assigned_by_map.items()}

        for d in docs:
            cid = d.get("class_id")
            sid = d.get("subject_id")
            tid = d.get("teacher_id")
            aid = d.get("assigned_by")

            if cid is not None:
                d["class_name"] = class_name_map.get(cid) or class_name_map_str.get(str(cid)) or "[deleted class]"

            if sid is not None:
                d["subject_label"] = subject_label_map.get(sid) or subject_label_map_str.get(str(sid)) or "[deleted subject]"

            if tid is not None:
                d["teacher_name"] = teacher_name_map.get(tid) or teacher_name_map_str.get(str(tid)) or "[deleted teacher]"

            if aid is not None:
                d["assigned_by_username"] = assigned_by_map.get(aid) or assigned_by_map_str.get(str(aid)) or ""

        return docs


    def schedule_slot_packs_for_ids(
        self,
        slot_ids: Iterable[ObjectId | str | dict | None],
    ) -> Dict[ObjectId, ScheduleSlotPack]:
        """
        Requires a schedule read model. If you don't have one yet, implement:
        - schedule_read_model.list_slots_by_ids(oids) -> list[dict]
        Each slot doc should contain:
        - _id, day_of_week, start_time, end_time, room
        """
        if not hasattr(self, "schedule_read_model") or self.schedule_read_model is None:
            return {}

        oids = self._normalize_ids(slot_ids)
        if not oids:
            return {}

        docs = self.schedule_read_model.list_slots_by_ids(oids)

        mapping: Dict[ObjectId, ScheduleSlotPack] = {}
        for d in docs:
            _id = d.get("_id")
            if _id is None:
                continue

            mapping[_id] = {
                "day_of_week": d.get("day_of_week"),
                "start_time": d.get("start_time"),
                "end_time": d.get("end_time"),
                "room": d.get("room"),
            }

        return mapping

    def teacher_select_options_for_ids(
        self,
        teacher_user_ids: Iterable[ObjectId | str | dict | None],
        *,
        include_label: bool = True,
        fallback_label: str = "[deleted teacher]",
    ) -> List[Dict[str, Any]]:
        """
        Build UI-friendly select options for teachers:

        [
          { "value": "ObjectIdString", "label": "Teacher Name", "name": "Teacher Name" }
        ]

        Notes:
        - Expects IDs to be the same "user_id" keys used by StaffReadModel.
        - Handles ids coming as ObjectId, str, or {"$oid": "..."}.
        """
        oids = self._normalize_ids(teacher_user_ids)
        if not oids:
            return []

        # staff_names_for_ids returns: {user_id(ObjectId) -> staff_name(str)}
        name_map = self.staff_names_for_ids(oids)
        name_map_str = {str(k): v for k, v in name_map.items()}

        options: List[Dict[str, Any]] = []
        for oid in oids:
            name = name_map.get(oid) or name_map_str.get(str(oid)) or ""
            label = (name or "").strip() or fallback_label

            options.append(
                {
                    "value": str(oid),
                    "label": label if include_label else label,  # keep shape stable
                    "name": label,
                }
            )

        # Stable UI ordering
        options.sort(key=lambda x: (x.get("label") or "").lower())
        return options