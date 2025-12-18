from pymongo.database import Database
from bson import ObjectId
from typing import List, Tuple, Union , Optional
from app.contexts.iam.domain.iam import  IAM
from app.contexts.iam.factory.iam_factory import IAMFactory
from app.contexts.admin.read_models.admin_read_model import AdminReadModel
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.admin.data_transfer.request import (
    AdminCreateUserSchema,
    AdminUpdateUserSchema,
    AdminSetUserStatusSchema,
)

from app.contexts.iam.repositories.iam_repositorie import MongoIAMRepository
from app.contexts.iam.policies.iam_uniqueness_policy import IAMUniquenessPolicy
from app.contexts.shared.model_converter import mongo_converter
from app.contexts.iam.mapper.iam_mapper import IAMMapper 
from app.contexts.iam.error.iam_exception import NotFoundUserException
from app.contexts.auth.services import AuthService




from app.contexts.iam.services.iam_lifecycle_service import IAMLifecycleService



class UserAdminService:
    def __init__(self, db: Database):
        self._iam_repository = MongoIAMRepository(db["iam"])
        self._iam_read_model = IAMReadModel(db)
        self._admin_read_model = AdminReadModel(db)
        self._auth_service = AuthService()
        self._iam_mapper = IAMMapper()

        self._uniqueness_policy = IAMUniquenessPolicy(self._iam_read_model)
        self._iam_factory = IAMFactory(iam_read_model=self._iam_read_model)
        self._iam_lifecycle_service = IAMLifecycleService(db)

    def admin_create_user(self, payload: AdminCreateUserSchema, created_by: str | ObjectId) -> IAM:
        created_by_oid = mongo_converter.convert_to_object_id(created_by)
        iam = self._iam_factory.create_user(
            email=payload.email,
            password=payload.password,
            username=payload.username,
            role=payload.role,
            created_by=created_by_oid,
        )
        return self._iam_repository.save(self._iam_mapper.to_persistence(iam))

    def admin_update_user(self, user_id: str | ObjectId, payload: AdminUpdateUserSchema) -> IAM:
        user_oid = mongo_converter.convert_to_object_id(user_id)
        iam = self._iam_repository.find_one(user_oid)
        if not iam:
            raise NotFoundUserException(str(user_id))
        new_username = payload.username if payload.username and payload.username != iam.username else None
        new_email = payload.email if payload.email and payload.email != iam.email else None
        self._uniqueness_policy.ensure_unique(
            username=new_username,
            email=new_email,
            exclude_user_id=user_oid,
        )
        hashed_password = None
        if payload.password:
            hashed_password = self._auth_service.hash_password(payload.password)

        iam.update_info(email=payload.email, username=payload.username, password=hashed_password)
        return self._iam_repository.update(user_oid, self._iam_mapper.to_persistence(iam))


    def admin_soft_delete_user(self, user_id: str | ObjectId, deleted_by: str | ObjectId) -> bool:
        user_oid = mongo_converter.convert_to_object_id(user_id)
        deleted_by_oid = mongo_converter.convert_to_object_id(deleted_by)
        self._iam_lifecycle_service.soft_delete_user(user_oid, deleted_by_oid)
        return True

    def admin_restore_user(self, user_id: str | ObjectId, actor_id: str | ObjectId) -> bool:
        user_oid = mongo_converter.convert_to_object_id(user_id)
        actor_oid = mongo_converter.convert_to_object_id(actor_id)
        self._iam_lifecycle_service.restore_user(user_oid, actor_oid)
        return True

    def admin_set_user_status(self, user_id: str | ObjectId, schema: AdminSetUserStatusSchema) -> dict:
        user_oid = mongo_converter.convert_to_object_id(user_id)
        self._iam_lifecycle_service.set_user_status(user_oid, schema.status)
        return {"id": str(user_oid), "status": schema.status.value}

    def admin_get_users(self, role: Union[str, list[str]], page: int, page_size: int, search: Optional[str] = None,) -> Tuple[List[dict], int]:
        cursor, total = self._admin_read_model.get_page_by_role(
            role, page=page, page_size=page_size, search=search
        )
        return cursor, total
