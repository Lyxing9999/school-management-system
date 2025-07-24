from app.models.user import UserModel
from app.enums.roles import Role
from app.utils.objectid import ObjectId # type: ignore
from typing import TypedDict, Optional, Dict, Any, Union, Literal
from werkzeug.security import generate_password_hash  # type: ignore
from app.models.student import StudentModel
import logging
from abc import ABC, abstractmethod
from app.utils.dict_utils import flatten_dict # type: ignore
from app.models.teacher import TeacherModel
from datetime import datetime
from app.error.exceptions import NotFoundError, PydanticValidationError, BadRequestError, InternalServerError, AppBaseException, ErrorSeverity, ErrorCategory  # type: ignore 
from pymongo.database import Database # type: ignore
from app.utils.date_utils import ensure_date
from app.repositories.user_repository import  UserRepositoryImpl, get_user_repository
from app.utils.pyobjectid import PyObjectId
from app.services.base.base_utils_service import BaseServiceUtils
logger = logging.getLogger(__name__)

class UpdateRoleInfoResponse(TypedDict):
    role: str
    update_data: dict
    original_data: dict



class UserServiceConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "users"




class UserService(ABC):
    @property
    @abstractmethod
    def user_repo(self) -> UserRepositoryImpl:
        pass

class MongoUserService(UserService):
    def __init__(self, config: UserServiceConfig):
        self.config = config
        self.db = self.config.db
        self.collection = self.db[self.config.collection_name]
        self.utils = BaseServiceUtils(self.db, UserModel)
        self._user_repo = get_user_repository(self.db)
        self._role_collections = {
            Role.TEACHER.value: self.db[TeacherModel._collection_name],
            Role.STUDENT.value: self.db[StudentModel._collection_name],
            Role.ADMIN.value: self.db[UserModel._collection_name]
        }
    def _get_role_collection(self, role: str):
        collection = self._role_collections.get(role)
        if collection is None:
            raise InternalServerError(f"Collection for role '{role}' not found")
        return collection     

    @property
    def user_repo(self) -> UserRepositoryImpl:
        return self._user_repo
      


    
    @staticmethod
    def ensure_date(value: Any) -> Any:
        return ensure_date(value)

    def _update_role_info(self, role: str, update_data: Dict[str, Any], original_data: Dict[str, Any]) -> UpdateRoleInfoResponse:
        if role == Role.STUDENT.value:
            student_role_data = (
                update_data.get("student_info") 
                or update_data.get("student_info") 
                or original_data.get("student_info", {})
            )
            birth_date = student_role_data.get("birth_date")
            student_role_data["birth_date"] = ensure_date(birth_date) if birth_date else None
            student_role_data["updated_at"] = self.utils.now
            update_data["student_info"] = student_role_data
            update_data.pop("student", None)
        elif role == Role.TEACHER.value:
            teacher_info = update_data.get("teacher_info") or original_data.get("teacher_info", {})
            teacher_info["updated_at"] = self.utils.now
            update_data.setdefault("phone_number", original_data.get("phone_number"))
            update_data["teacher_info"] = teacher_info
            update_data.pop("teacher", None)
        return UpdateRoleInfoResponse(role=role, update_data=update_data, original_data=original_data)


    def _create_role_specific_data(self, _id: ObjectId, role: Union[Role, str]) -> None:
        """Create minimal role-specific data for a new user based on their role."""
        if isinstance(role, str):
            role = Role(role)
        role_collection = self._get_role_collection(role)
        if role == Role.STUDENT:
            new_student = StudentModel.create_minimal(_id=PyObjectId(_id))
            data = new_student.model_dump(by_alias=True)
        elif role == Role.TEACHER:
            new_teacher = TeacherModel.create_minimal(_id=PyObjectId(_id))
            data = new_teacher.model_dump(by_alias=True)
        elif role == Role.ADMIN:
            data = {"_id": _id}
        data["_id"] = data.pop("id", None) or _id

        logger.info(f"Creating {role} info for user_id: {_id}")
        role_collection.insert_one(data)


    def create_user(self, data: dict) -> UserModel:  
        data["created_at"] = datetime.utcnow()
        if "password" in data and data["password"]:
            data["password"] = generate_password_hash(data["password"])
        username = data.get("username")
        email = data.get("email")
        role = data.get("role", Role.STUDENT.value)

        if role not in [r.value for r in Role]:
            raise BadRequestError(message="Invalid role provided", details={"role": role}, user_message="The specified user role is invalid.", status_code=400)
        try:
            if username and self.collection.find_one({"username": username}):
                raise BadRequestError(message="Username already exists", details={"username": username}, user_message="The username is already teken. Please choose another.", status_code=400)
            if email and self.collection.find_one({"email": email}):
                raise BadRequestError(message="Email already exists", details={"email": email}, user_message="The email is  already registered. Please choose another.", status_code=400)
            result = self.collection.insert_one(data)
            if not result.acknowledged:
                raise InternalServerError(message="Failed to create user in database", details={"data": data}, status_code=500)
            _id = result.inserted_id
            self._create_role_specific_data(_id, role)
            data["id"] = str(_id)
            data.pop("password", None)  
            to_model = self.utils.to_response_model(data)
            if to_model is None:
                raise NotFoundError(message="User not found", resource_type="User", resource_id=str(_id), user_message="User not found in the system.", status_code=404, severity=ErrorSeverity.LOW, category=ErrorCategory.DATABASE)
            return to_model
        except AppBaseException:
            raise 
        except Exception as e:
            raise InternalServerError(message="Failed to create user", cause=e, details={"data": data}, status_code=500, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE)

    def patch_user(self, _id: Union[str, ObjectId], update_data: Dict[str, Any]) -> Optional[UserModel]:
        if not update_data:
            raise BadRequestError(
                message="No update data provided",
                user_message="Please provide fields to update.",
                status_code=400,
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.VALIDATION
            )
        user_id = self.utils._validate_objectid(_id)
        update_data = self.utils._prepare_safe_update(update_data)
        if update_data.get("password"):
            update_data["password"] =  generate_password_hash(update_data["password"])
        query = {"_id": user_id}
        existing_user = self.collection.find_one(query)
        if not existing_user:
            raise NotFoundError(
                message="User not found",
                status_code=404,
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.DATABASE,
                details={"user_id": str(user_id)}
            )
        if "username" in update_data:
            query = {
                "username": update_data["username"],
                "_id": {"$ne": user_id}  
            }
            conflict = self.collection.find_one(query)
            if conflict:
                raise BadRequestError(
                    message="Username already taken by another user",
                    details={"username": update_data["username"]},
                    status_code=400,
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.VALIDATION
                )
        email = update_data.get("email")
        if email not in [None, ""]:
            query = {
                "email": email,
                "_id": {"$ne": user_id}
            }
            conflict = self.collection.find_one(query)
            if conflict:
                raise BadRequestError(
                    message="Email already taken by another user",
                    details={"email": email},
                    status_code=400,
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.VALIDATION
                )
        try:
            update_data["updated_at"] = self.utils.now
            query = {"_id": user_id}
            result = self.collection.update_one(query, update_data)
            if result.matched_count > 0:
                updated_user = self.collection.find_one(query)
                if updated_user:
                    return self.utils.to_response_model(updated_user)
                raise NotFoundError(message="User not found", resource_type="User", resource_id=str(user_id), user_message="User not found in the system.", status_code=404, severity=ErrorSeverity.LOW, category=ErrorCategory.DATABASE)
            raise InternalServerError(
                message="Update failed. No document was matched.",
                details={"_id": str(user_id)},
                user_message="We couldn't update the user. Please try again later."
            )
        except AppBaseException as e:
            raise e
        except Exception as e:
            raise InternalServerError(message="Failed to update user", cause=e, details={"user_id": str(user_id), "update_data": update_data}, status_code=500, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE)


    def delete_user(self, _id: str) -> Literal[True]:
        validated_id = self.utils._validate_objectid(_id)
        query = {"_id": validated_id}
        result = self.collection.delete_one(query)
        if result.deleted_count > 0:
            return True
        raise InternalServerError(
            message="User deletion failed; no documents deleted.",
            details={"_id": _id},
            user_message="Could not delete the user. Please try again later."
        )


  
    def patch_user_detail(self, _id: Union[str, ObjectId], user_update_data: dict) -> Optional[dict]:
        if not _id or not user_update_data:
            raise BadRequestError(
                message="Invalid request",
                user_message="Please provide a valid user ID and update data.",
                status_code=400,
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.VALIDATION
            )
        obj_id = self.utils._validate_objectid(_id)
        try:
            full_user = self._user_repo.find_user_detail(obj_id) if self._user_repo else self.collection.find_one({"_id": obj_id})
            if not full_user:
                raise NotFoundError(
                    message="User not found",
                    resource_type="User",
                    resource_id=str(obj_id),
                    user_message="User not found in the system."
                )
            base_user = full_user["data"]
            role = full_user["role"]
            role_collection = self._get_role_collection(role)
            safe_update = self.utils._prepare_safe_update(dict(user_update_data))
            if base_user is None:
                base_user = {}
            result = self._update_role_info(role, safe_update, base_user)
            flat_update = flatten_dict(result["update_data"])
            attendance_prefix = "student.attendance_record."
            keys_to_remove = [k for k in flat_update if k.startswith(attendance_prefix)]
            for key in keys_to_remove:
                flat_update.pop(key)
            full_attendance = user_update_data.get("student", {}).get("attendance_record")
            if full_attendance is not None:
                flat_update["student.attendance_record"] = full_attendance
            update_result = role_collection.update_one({"_id": obj_id}, {"$set": flat_update})
            if not update_result.modified_count > 0:
                raise BadRequestError(
                    message="No changes detected",
                    user_message="Nothing was updated because the data is the same.",
                    status_code=400,
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.VALIDATION
                )
            else:
                return {"status": True, "msg": "User info updated successfully"}
        except AppBaseException:
            raise  

        except Exception as e:
            raise InternalServerError(
                message="Unexpected error while updating user detail",
                cause=e,
                context={"_id": str(_id)}
            )

  


def get_user_service(db: Database) -> MongoUserService:
    return MongoUserService(UserServiceConfig(db))






