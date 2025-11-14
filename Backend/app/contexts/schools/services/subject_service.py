from typing import Union, List
from bson import ObjectId
from pymongo.database import Database
from app.contexts.schools.models.subject import SchoolSubject
from app.contexts.schools.repositories.subject_repo import SubjectRepository
from app.contexts.schools.read_models.subject_read_model import SubjectReadModel
from app.contexts.schools.data_transfer.requests.subject_requests import SubjectCreateSchema, SubjectUpdateSchema
from app.contexts.schools.data_transfer.responses.subject_responses import SubjectBaseDataDTO
from app.contexts.core.log.log_service import LogService
from app.contexts.schools.error.subject_exceptions import SubjectCreateException, SubjectValueException


class SubjectService:
    def __init__(self, db: Database):
        self._subject_repo = SubjectRepository(db)
        self._subject_read_model = SubjectReadModel(db)
        self._log_service = LogService.get_instance()

    def _log(self, operation: str, subject_id: str | None = None, extra: dict | None = None, level: str = "INFO"):
        msg = f"SubjectService::{operation}" + (f" [subject_id={subject_id}]" if subject_id else "")
        self._log_service.log(msg, level=level, module="SubjectService", extra=extra or {})

    def get_subject_to_domain(self, subject_id: Union[str, ObjectId]) -> SchoolSubject:
        if isinstance(subject_id, str):
            subject_id = ObjectId(subject_id)
        subject_model = self._subject_read_model.find_by_id(subject_id)
        if not subject_model:
            raise SubjectValueException(f"Subject not found: {subject_id}")
        return SchoolSubject.to_domain(subject_model)

    # -------------------------
    # CRUD
    # -------------------------
    def find_all_subjects_dto(self) -> list[dict]:
        subjects = self._subject_read_model.get_subjects()
        return [SchoolSubject.to_domain(s).to_dto().model_dump() for s in subjects]

    def find_subject_by_id_dto(self, subject_id: str | ObjectId) -> dict:
        subject_obj = self._subject_read_model.find_by_id(ObjectId(subject_id) if isinstance(subject_id, str) else subject_id)
        return SchoolSubject.to_domain(subject_obj).to_dto()

    def create_subject(self, payload: SubjectCreateSchema, created_by: ObjectId) -> SubjectBaseDataDTO:
        domain_subject = SchoolSubject.from_create_schema(payload, created_by)
        saved_id = self._subject_repo.save(domain_subject.to_persistence_dict())
        if not saved_id:
            raise SubjectCreateException("Failed to save subject")
        domain_subject.id = saved_id
        return domain_subject.to_dto()

    def update_subject(self, subject_id: str | ObjectId, payload: SubjectUpdateSchema) -> SubjectBaseDataDTO:
        domain_subject = self.get_subject_to_domain(subject_id)
        domain_subject.name = payload.name
        if payload.teacher_ids:
            domain_subject.set_teachers(payload.teacher_ids)
        self._subject_repo.save(domain_subject.to_persistence_dict())
        return domain_subject.to_dto()

    def remove_teacher_from_subject(self, subject_id: str | ObjectId, teacher_id: ObjectId) -> SubjectBaseDataDTO:
        domain_subject = self.get_subject_to_domain(subject_id)
        domain_subject.remove_teacher(teacher_id)
        self._subject_repo.save(domain_subject.to_persistence_dict())
        return domain_subject.to_dto()
        
    def delete_subject(self, subject_id: str | ObjectId) -> SubjectBaseDataDTO:
        domain_subject = self.get_subject_to_domain(subject_id)
        domain_subject.mark_deleted()
        self._subject_repo.save(domain_subject.to_persistence_dict())
        return domain_subject.to_dto()