from typing import Dict, Any, Union, List, Optional
from bson import ObjectId
from pymongo.database import Database

from app.contexts.shared.model_converter import mongo_converter
from app.contexts.shared.lifecycle.filters import not_deleted, ShowDeleted
from app.contexts.shared.lifecycle.errors import LifecyclePolicyDeniedException

from app.contexts.school.domain.teaching_assignment import TeachingAssignmentRecord
from app.contexts.school.repositories.teacher_assignment_repository import TeacherAssignmentRepository
from app.contexts.school.read_models.teacher_assignment_read_model import TeacherAssignmentReadModel

from app.contexts.shared.services.display_name_service import DisplayNameService


class DuplicateAssignmentException(Exception):
    pass


class TeachingAssignmentAdminService:
    def __init__(self, db: Database, display: Optional[DisplayNameService] = None):
        self.db = db
        self.repo = TeacherAssignmentRepository(db)
        self.read = TeacherAssignmentReadModel(db)

        self.classes = db["classes"]
        self.subjects = db["subjects"]

        self.display = display

    def _oid(self, v: Union[str, ObjectId]) -> ObjectId:
        return mongo_converter.convert_to_object_id(v)

    def _normalize_docs(self, docs: List[dict]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for d in docs:
            x = dict(d)

            if "id" not in x and x.get("_id") is not None:
                x["id"] = str(x["_id"])

            for k in ("class_id", "subject_id", "teacher_id", "assigned_by"):
                if x.get(k) is not None:
                    x[k] = str(x[k])

            normalized.append(x)
        return normalized

    # -------------------------
    # LIST (UI)
    # -------------------------
    def list_assignments_for_class(
        self,
        *,
        class_id: str | ObjectId,
        show_deleted: ShowDeleted = "active",
        enrich: bool = True,
    ) -> List[Dict[str, Any]]:
        docs = self.read.list_for_class(self._oid(class_id), show_deleted=show_deleted)
        docs = self._normalize_docs(docs)
        if enrich and self.display is not None:
            docs = self.display.enrich_teaching_assignments(docs)
        return docs

    def list_assignments_for_teacher(
        self,
        *,
        teacher_id: str | ObjectId,
        show_deleted: ShowDeleted = "active",
        enrich: bool = True,
    ) -> List[Dict[str, Any]]:
        docs = self.read.list_for_teacher(self._oid(teacher_id), show_deleted=show_deleted)
        docs = self._normalize_docs(docs)
        if enrich and self.display is not None:
            docs = self.display.enrich_teaching_assignments(docs)
        return docs

    # -------------------------
    # ASSIGN (WRITE)
    # Behavior:
    # - One active teacher per (class, subject).
    # - Teacher can have many subjects (no limit).
    # -------------------------
    def assign_subject_teacher(
        self,
        *,
        class_id: str | ObjectId,
        subject_id: str | ObjectId,
        teacher_id: str | ObjectId,
        actor_id: str | ObjectId | None = None,
        overwrite: bool = True,
    ) -> Dict[str, Any]:
        cid = self._oid(class_id)
        sid = self._oid(subject_id)
        tid = self._oid(teacher_id)
        aid = self._oid(actor_id) if actor_id else None

        # Validate class exists (active)
        cls = self.classes.find_one(not_deleted({"_id": cid}), {"_id": 1, "status": 1})
        if not cls:
            raise LifecyclePolicyDeniedException(
                entity="class",
                entity_id=str(cid),
                mode="assign",
                reasons={"class": "not_found_or_deleted"},
                recommended={},
            )

        # Validate subject exists + active
        subj = self.subjects.find_one(not_deleted({"_id": sid}), {"_id": 1, "is_active": 1})
        if not subj:
            raise LifecyclePolicyDeniedException(
                entity="subject",
                entity_id=str(sid),
                mode="assign",
                reasons={"subject": "not_found_or_deleted"},
                recommended={},
            )
        if subj.get("is_active") is False:
            raise LifecyclePolicyDeniedException(
                entity="subject",
                entity_id=str(sid),
                mode="assign",
                reasons={"subject": "inactive"},
                recommended={},
            )

        existing = self.read.get_active_by_class_subject(cid, sid)

        # If already assigned and overwrite is disabled -> reject
        if existing and not overwrite:
            raise DuplicateAssignmentException("This subject already has an assigned teacher in this class.")

        # If already assigned and overwrite is enabled -> update teacher
        if existing and overwrite:
            existing_id = existing.get("_id")
            rec = self.repo.find_by_id(existing_id, show_deleted="active") if existing_id else None

            # safety fallback
            if rec is None:
                rec = TeachingAssignmentRecord(
                    class_id=cid,
                    subject_id=sid,
                    teacher_id=tid,
                    assigned_by=aid,
                )
                self.repo.insert(rec)
                return {"assignment_id": str(rec.id), "created": True, "modified_count": 1}

            # If same teacher assigned again, you may treat as no-op
            if rec.teacher_id == tid:
                return {"assignment_id": str(rec.id), "created": False, "modified_count": 0}

            rec.change_teacher(tid, actor_id=aid)
            self.repo.update(rec)
            return {"assignment_id": str(rec.id), "created": False, "modified_count": 1}

        # Create new assignment (subject not assigned yet)
        rec = TeachingAssignmentRecord(
            class_id=cid,
            subject_id=sid,
            teacher_id=tid,
            assigned_by=aid,
        )
        self.repo.insert(rec)
        return {"assignment_id": str(rec.id), "created": True, "modified_count": 1}

    # -------------------------
    # UNASSIGN (WRITE)
    # -------------------------
    def unassign_subject_teacher(
        self,
        *,
        class_id: str | ObjectId,
        subject_id: str | ObjectId,
        actor_id: str | ObjectId,
    ) -> Dict[str, Any]:
        cid = self._oid(class_id)
        sid = self._oid(subject_id)
        aid = self._oid(actor_id)

        modified_count = self.repo.soft_delete_by_class_subject(
            class_id=cid,
            subject_id=sid,
            actor_id=aid,
        )

        return {"deleted": bool(modified_count), "modified_count": int(modified_count)}