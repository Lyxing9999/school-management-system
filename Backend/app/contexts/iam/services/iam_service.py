from typing import Union
from pymongo.database import Database
from app.contexts.iam.repositories.iam_repositorie import MongoIAMRepository
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.iam.auth.services import AuthService
from app.contexts.iam.data_transfer.response import IAMResponseDataDTO, IAMBaseDataDTO
from app.contexts.iam.error.iam_exception import (
    NotFoundUserException,
    UserDeletedException,
    InvalidPasswordException,
    UserInactiveException,
)
from app.contexts.iam.auth.refresh_utils import (
    create_refresh_token,
    hash_refresh_token,
    now_utc,
    REFRESH_TTL,
)
class IAMService:
    """Identity & Access Management Service"""

    def __init__(self, db: Database):
        self.db = db
        self._iam_repository = MongoIAMRepository(db["iam"]) 
        self._iam_read_model = IAMReadModel(db) 
        self._auth_service = AuthService()  # auth helper (hash, token)
        self._iam_mapper = IAMMapper()  # map raw dict <-> domain <-> DTO
        self._refresh_tokens = db["refresh_tokens"]  

    # -------------------------
    # Login IAM User
    # -------------------------
    def login(self, email: str, password: str) -> Union[IAMResponseDataDTO, tuple]:
        raw_user = self._iam_read_model.get_by_email(email)  # query by email
        if not raw_user:
            raise NotFoundUserException(email)  # raise if not found
        iam_model = self._iam_mapper.to_domain(raw_user)  # map to domain
        if iam_model.is_deleted():
            raise UserDeletedException(email)  # deleted check
        if iam_model.is_inactive():
            raise UserInactiveException(email)  # inactive check
        if not iam_model.check_password(password, self._auth_service):  # password check
            raise InvalidPasswordException(password)
        safe_dict = self._iam_mapper.to_safe_dict(iam_model)  # prepare safe dict
        access = self._auth_service.create_access_token(safe_dict)
        refresh = create_refresh_token()

        self._refresh_tokens.insert_one({
            "user_id": str(safe_dict["id"]),
            "token_hash": hash_refresh_token(refresh),
            "created_at": now_utc(),
            "expires_at": now_utc() + REFRESH_TTL,
            "revoked_at": None,
            "replaced_by_hash": None,
        })
        
        dto = IAMResponseDataDTO(
            user=IAMBaseDataDTO(**safe_dict),
            access_token=access
        )
        
        return dto, refresh

    def me(self, user_id: str) -> IAMBaseDataDTO:
        raw_user = self._iam_read_model.get_active_by_id(user_id)
        if not raw_user:
            raise NotFoundUserException(user_id)

        iam_model = self._iam_mapper.to_domain(raw_user)
        if iam_model.is_deleted():
            raise UserDeletedException(user_id)
        if iam_model.is_inactive():
            raise UserInactiveException(user_id)

        safe_dict = self._iam_mapper.to_safe_dict(iam_model)
        return IAMBaseDataDTO(**safe_dict)

    # -------------------------
    # TODO 
    # implement
    # rate limit    
    # security
    # login google 
    # -------------------------