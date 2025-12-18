from pymongo.database import Database
from app.contexts.iam.repositories.iam_repositorie import MongoIAMRepository
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.iam.mapper.iam_mapper import IAMMapper
from app.contexts.auth.services import AuthService
from app.contexts.iam.data_transfer.response import IAMResponseDataDTO, IAMBaseDataDTO
from app.contexts.iam.error.iam_exception import (
    NotFoundUserException,
    UserDeletedException,
    InvalidPasswordException,
    UserSuspendedException,
    UserInactiveException,


)
class IAMService:
    """Identity & Access Management Service"""

    def __init__(self, db: Database):
        self.db = db
        self._iam_repository = MongoIAMRepository(db["iam"]) 
        self._iam_read_model = IAMReadModel(db) 
        self._auth_service = AuthService()  # auth helper (hash, token)
        self._iam_mapper = IAMMapper()  # map raw dict <-> domain <-> DTO



    # -------------------------
    # Login IAM User
    # -------------------------
    def login(self, email: str, password: str) -> IAMResponseDataDTO:
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
        token = self._auth_service.create_access_token(safe_dict)  # generate token
        return IAMResponseDataDTO(user=IAMBaseDataDTO(**safe_dict), access_token=token)  # return response



    # -------------------------
    # TODO 
    # implement
    # rate limit    
    # security
    # login google 
    # -------------------------