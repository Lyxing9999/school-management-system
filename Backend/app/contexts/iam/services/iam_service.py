from time import time
from pymongo.database import Database
from bson import ObjectId
from app.contexts.iam.repositories.iam_repositorie import IAMRepository
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.iam.domain.iam import IAM
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.auth.services import AuthService
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.core.log.log_service import LogService
from app.contexts.iam.data_transfer.request import IAMUpdateSchema
from app.contexts.iam.data_transfer.response import IAMResponseDataDTO, IAMBaseDataDTO
from app.contexts.iam.error.iam_exception import (
    NotFoundUserException,
    UserDeletedException,
    NoChangeAppException,
    InvalidPasswordException,
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
)

class IAMService:
    """Identity & Access Management Service"""

    def __init__(self, db: Database):
        self.db = db
        self.mongo_converter = mongo_converter 
        self._iam_repository = IAMRepository(db) 
        self._iam_read_model = IAMReadModel(db) 
        self._auth_service = AuthService()  # auth helper (hash, token)
        self._iam_mapper = IAMMapper()  # map raw dict <-> domain <-> DTO
        self._log_service = LogService.get_instance()  # singleton log service

    # -------------------------
    # Logging helper
    # -------------------------
    def _log(self, operation: str, user_id: str | None = None, extra: dict | None = None, level: str = "INFO"):
        msg = f"IAMService::{operation}" + (f" [user_id={user_id}]" if user_id else "")  # construct message
        self._log_service.log(msg, level=level, module="IAMService", user_id=user_id, extra=extra or {})  # send to logger

    # -------------------------
    # Validate unique username/email
    # -------------------------
    def _validate_unique_fields(self, username: str | None = None, email: str | None = None, exclude_user_id: ObjectId | None = None):
        query = {"$or": []}  # initialize OR query
        if username: query["$or"].append({"username": username})  # check username
        if email: query["$or"].append({"email": email})  # check email
        if not query["$or"]:
            return 
        if exclude_user_id: query = {"$and": [{"_id": {"$ne": exclude_user_id}}, query]}  # exclude current user
        existing_user = self._iam_repository.find_one(query)  # query db
        if existing_user:  # if conflict
            if username and existing_user.get("username") == username:
                raise UsernameAlreadyExistsException(username)  # raise error
            if email and existing_user.get("email") == email:
                raise EmailAlreadyExistsException(email)

    # -------------------------
    # Get IAM Domain Model
    # -------------------------
    def get_user_to_domain(self, user_id: str | ObjectId) -> IAM:
        start = time()  # start timer
        user_id_obj = mongo_converter.convert_to_object_id(user_id)  # convert to ObjectId
        raw_user = self._iam_read_model.get_by_id(user_id_obj)  # get raw dict
        duration_ms = (time() - start) * 1000  # measure duration
        self._log("get_user_to_domain", user_id=str(user_id), extra={"duration_ms": duration_ms})  # log operation
        if not raw_user: raise NotFoundUserException(user_id)  # raise if missing
        return self._iam_mapper.to_domain(raw_user)  # map to domain

    # -------------------------
    # Login IAM User
    # -------------------------
    def login(self, email: str, password: str) -> IAMResponseDataDTO:
        start = time()  # start timer
        raw_user = self._iam_read_model.get_by_email(email)  # query by email
        if not raw_user:
            raise NotFoundUserException(email)  # raise if not found
        iam_model = self._iam_mapper.to_domain(raw_user)  # map to domain
        if iam_model.is_deleted():
            raise UserDeletedException(email)  # deleted check
        if not iam_model.check_password(password, self._auth_service):  # password check
            self._log("login_failed", extra={"email": email}, level="WARNING")  # log failed attempt
            raise InvalidPasswordException(password)
        safe_dict = self._iam_mapper.to_safe_dict(iam_model)  # prepare safe dict
        token = self._auth_service.create_access_token(safe_dict)  # generate token
        duration_ms = (time() - start) * 1000  # log duration
        self._log("login", user_id=str(iam_model.id), extra={"duration_ms": duration_ms, "email": email})
        return IAMResponseDataDTO(user=IAMBaseDataDTO(**safe_dict), access_token=token)  # return response

    # -------------------------
    # Update profile
    # -------------------------
    def update_info(self, user_id: str | ObjectId, update_schema: IAMUpdateSchema, *, update_by_admin: bool = False) -> IAM:
        start = time()  # start timer
        iam_model = self.get_user_to_domain(user_id)  # fetch domain model
        if update_schema.password is not None:
            iam_model.password = self._auth_service.hash_password(update_schema.password)
        self._validate_unique_fields(
            username=update_schema.username,
            email=update_schema.email,
            exclude_user_id=mongo_converter.convert_to_object_id(iam_model.id)
        )
        iam_model.update_info(email=update_schema.email, username=update_schema.username)
        modified_count = self._iam_repository.update(
            mongo_converter.convert_to_object_id(iam_model.id),
            self._iam_mapper.to_persistence(iam_model)
        )
        if modified_count == 0:
            raise NoChangeAppException()  
        duration_ms = (time() - start) * 1000
        self._log("update_info", user_id=str(user_id), extra={"duration_ms": duration_ms, "update_by_admin": update_by_admin})
        return iam_model

    # -------------------------
    # Soft delete user
    # -------------------------
    def soft_delete(self, user_id: str | ObjectId, deleted_by: str | ObjectId | None = None) -> IAM:
        start = time()
        iam_model = self.get_user_to_domain(user_id)  # fetch domain
        deleted_by_obj = mongo_converter.convert_to_object_id(deleted_by) if deleted_by else None  # optional deleted_by
        iam_model.soft_delete(deleted_by_obj)  # update domain
        modified_count = self._iam_repository.soft_delete(mongo_converter.convert_to_object_id(iam_model.id), deleted_by_obj)  # persist
        if modified_count == 0:
            raise NoChangeAppException("User already deleted in DB")  # check result
        duration_ms = (time() - start) * 1000
        self._log("soft_delete", user_id=str(user_id), extra={"duration_ms": duration_ms, "deleted_by": str(deleted_by_obj) if deleted_by else None})  # log
        return iam_model  # return DTO

    # -------------------------
    # Hard delete user
    # -------------------------
    def hard_delete(self, user_id: str | ObjectId) -> bool:
        start = time()
        deleted_count = self._iam_repository.hard_delete(mongo_converter.convert_to_object_id(user_id))  # delete
        duration_ms = (time() - start) * 1000
        self._log("hard_delete", user_id=str(user_id), extra={"duration_ms": duration_ms})  # log
        return deleted_count > 0  # return boolean

    # -------------------------
    # Save domain
    # -------------------------
    def save_domain(self, iam_model: IAM) -> IAM:
        """Persist a domain object and return updated domain with ID."""
        self._validate_unique_fields(
            username=iam_model.username,
            email=iam_model.email,
            exclude_user_id=iam_model.id
        )
        saved_id = self._iam_repository.save(self._iam_mapper.to_persistence(iam_model))
        iam_model.id = saved_id
        return iam_model