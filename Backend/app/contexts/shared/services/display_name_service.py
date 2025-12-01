from __future__ import annotations
from typing import Iterable, Dict
from bson import ObjectId

from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.staff.read_model import StaffReadModel
from app.contexts.school.read_models.class_read_model import ClassReadModel
from app.contexts.school.read_models.subject_read_model import SubjectReadModel
from app.contexts.student.read_models.student_read_model import StudentReadModel
from app.contexts.shared.model_converter import mongo_converter


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

    # -----------------------------
    # internal
    # -----------------------------

    @staticmethod
    def _normalize_ids(ids: Iterable[ObjectId | str | None]) -> list[ObjectId]:
        result: list[ObjectId] = []
        for raw in ids:
            if raw is None:
                continue
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
        user_ids: Iterable[ObjectId | str | None],
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

    # -----------------------------
    # STAFF (teachers)
    # -----------------------------

    def staff_names_for_user_ids(
        self,
        user_ids: Iterable[ObjectId | str | None],
    ) -> Dict[ObjectId, str]:
        """
        :return: {user_id -> staff_name}
        """
        oids = self._normalize_ids(user_ids)
        if not oids:
            return {}
        return self.staff_read_model.list_names_by_user_ids(oids)

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
        class_ids: Iterable[ObjectId | str | None],
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
        subject_ids: Iterable[ObjectId | str | None],
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

        class_ids: list[ObjectId | str] = []
        teacher_ids: list[ObjectId | str] = []
        subject_ids: list[ObjectId | str] = []

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
        teacher_name_map = self.staff_names_for_user_ids(teacher_ids)
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