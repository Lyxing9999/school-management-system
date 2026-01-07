
from bson import ObjectId
from pymongo.database import Database

from app.contexts.school.errors.subject_exceptions import (
    InvalidSubjectCodeError,
    InvalidSubjectNameError,
    SubjectCodeAlreadyExistsException,
    SubjectNameAlreadyExistsException,
)
from app.contexts.shared.lifecycle.filters import not_deleted


class SubjectUpdatePolicy:
    def __init__(self, db: Database):
        self.subjects = db["subjects"]

    def ensure_unique(
        self,
        *,
        subject_id: ObjectId,
        code: str | None = None,
        name: str | None = None,
    ) -> None:
        base_filter = not_deleted({"_id": {"$ne": subject_id}})

        if code is not None:
            normalized_code = code.strip().upper()
            if not normalized_code:
                raise InvalidSubjectCodeError(received_value=code)

            code_conflict = self.subjects.count_documents(
                {
                    **base_filter,
                    "code": normalized_code,
                },
                limit=1,
            )
            if code_conflict > 0:
                raise SubjectCodeAlreadyExistsException(received_value=normalized_code)

        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise InvalidSubjectNameError(received_value=name)

            name_conflict = self.subjects.count_documents(
                {
                    **base_filter,
                    "name": normalized_name,
                },
                limit=1,
            )
            if name_conflict > 0:
                raise SubjectNameAlreadyExistsException(received_value=normalized_name)