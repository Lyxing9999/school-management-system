
from app.utils.objectid import ObjectId # type: ignore
from typing import  Optional, List, Dict, Union, Tuple, Type,TypedDict, Any
from pydantic import BaseModel
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import logging
from app.shared.model_utils import default_model_utils
from app.error.exceptions import NotFoundError, PydanticValidationError, BadRequestError, InternalServerError, ErrorSeverity, ErrorCategory, AppBaseException, DatabaseError
from app.database.pipelines.user_pipeline import users_growth_by_role_pipeline, build_user_detail_pipeline, build_user_growth_stats_pipeline, build_search_user_pipeline, build_role_counts_pipeline
from pymongo.database import Database # type: ignore
from app.utils.convert import convert_objectid_to_str
from app.dtos.users.user_response_dto import UserResponseDTO , UserListResponseDTO
from app.dtos.teacher.teacher_response_dto import TeacherResponseDTO
from app.enum.enums import Role
from werkzeug.security import generate_password_hash
from app.repositories.base_repo import get_base_repository
from app.dtos.users.user_db_dto import UserDBDTO
from app.utils.convert import convert_objectid_to_str
class UserRepositoryConfig:
    def __init__(self, db: Database):
        self.db = db
        self.collection_name = "users"



class UserGrowthStatsResponse(TypedDict):
    date: str
    count: int
    percentage: float

class UserGrowthStateWithComparisonResponse(TypedDict):
    role: str
    previous: int
    current: int
    growth_percentage: float

logger = logging.getLogger(__name__)

class UserRepository(ABC):  
    @abstractmethod
    def find_user_by_username(self, username: str) -> Optional[UserResponseDTO]:
        pass
    
    @abstractmethod
    def find_all_users(self) -> UserListResponseDTO:
        pass
    
    @abstractmethod
    def find_user_detail(self, _id: Union[str, ObjectId]) -> UserResponseDTO:
        pass
    
    
class UserRepositoryImpl(UserRepository):
    def __init__(self, config: UserRepositoryConfig):
        self.config = config
        self.db = self.config.db
        self.collection = self.db[self.config.collection_name]
        self.utils = default_model_utils
        self._student_service = None
        self._teacher_service = None
        self._user_repo = get_base_repository(self.config)
 

    def role_model_map(self) -> Dict[str, Tuple[Type[BaseModel], str]]:
        return {
            Role.TEACHER.value: (TeacherResponseDTO, "teachers"),
            Role.STUDENT.value: (StudentResponseDTO, "students"),
            Role.ADMIN.value: (UserResponseDTO, "users")
        }
    @staticmethod
    def _parse_date_range( start: str, end: str) -> Tuple[datetime, datetime]:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)
            return start_dt, end_dt

    def _convert_objectid_to_str(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return convert_objectid_to_str(data)


    def find_user_by_username(self, username: str) -> UserDBDTO:
        user_data = self._user_repo.find_by_query({"username": username})
        if user_data is None:
            raise NotFoundError(
                message="User not found",
                details={"received_value": username},
                severity=ErrorSeverity.LOW,
                category=ErrorCategory.SYSTEM,
                status_code=404,
            )
        user_data = convert_objectid_to_str(user_data)
        return UserDBDTO.model_validate(user_data)

    def _handle_update_result(self, result, query, update_data) -> int:
        if result.modified_count > 0:
            return result.modified_count
        raise BadRequestError(
            message="No changes detected",
            details={"query": query, "update_data": update_data},
            user_message="Nothing was updated because the data is the same.",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.DATABASE,
            status_code=400
        )


    def find_user_by_id(self, _id: Union[str, ObjectId]) -> Optional[UserResponseDTO]:
        user_data = self._user_repo.find_by_query({"_id": _id})
        if user_data is None:
            raise NotFoundError(message="User not found", details={"_id": _id}, user_message="The user with the given id was not found.", hint="The user with the given id was not found. Please try again later.", status_code=404, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE)
        return user_data


    def update_user(self, query: Dict[str, Any], update_data: Dict[str, Any], hash_password: bool = False) -> int:
        if hash_password and "password" in update_data:
            update_data["password"] = generate_password_hash(update_data["password"])
        result = self.collection.update_one(query, {"$set": update_data})
        return self._handle_update_result(result, query, update_data)

    def find_user_by_id(self, id_str: str) -> Optional[UserResponseDTO]:
        if not id_str:
            raise BadRequestError(
                message="Invalid ObjectId",
                details={"received_value": id_str},
                status_code=400,
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.SYSTEM,
            )
        obj_id = self.utils.validate_object_id(id_str)
        try:
            user_data = self.collection.find_one({"_id": obj_id})
            if not user_data:
                raise NotFoundError(
                    message="User not found",
                    details={"received_value": id_str},
                    status_code=404,
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.DATABASE,
                )
            user_data.pop("password", None)
            user_data["_id"] = str(user_data["_id"])
            return UserResponseDTO.model_validate(user_data)
        except Exception as e:
            raise InternalServerError(
                message="Error fetching user by ID",
                cause=e,
                details={"received_value": id_str},
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
            )


            
    def find_all_users(self) -> UserListResponseDTO:
        """Find all users
        @return: List[UserModel]
        @throws: InternalServerError
        """
        try:
            users_cursor = self.collection.find()
            users_list = list(users_cursor)
            return UserListResponseDTO(users=users_list)
        except Exception as e:
            logger.error(f"Failed to fetch all users: {e}")
            raise InternalServerError(f"Failed to fetch all users: {e}")
        
        
    def search_user(self, query: str, page: int, page_size: int) ->  UserListResponseDTO:
        """Search for users by username or email
        @param query: str
        @param page: int
        @param page_size: int
        @return: List[UserModel]
        @throws: InternalServerError
        """
        try:
            pipeline = build_search_user_pipeline(query, page, page_size)
            users_cursor = self.collection.aggregate(pipeline)
            users_list = list(users_cursor)
            return UserListResponseDTO(users=users_list)
        except PydanticValidationError as e:
            raise e
        except Exception as e:
            raise InternalServerError(f"Failed to search users: {e}")
        
        
        
    def find_user_by_email(self, email: str) -> Optional[UserResponseDTO]:
        """Find a user by their email
        @param email: str
        @return: UserModel
        @throws: NotFoundError
        @throws: InternalServerError
        """
        try:
            user_data = self.collection.find_one({"email": email})
            if user_data:
                return self.utils.to_response_model(user_data)
            return None
        except Exception as e:
            logger.error(f"Failed to find user by email {email}: {e}")
            raise InternalServerError(f"Failed to find user by email {email}: {e}")
          
    
        

    def find_user_by_role(self, role: str) -> UserListResponseDTO:
        """Find users by their role
        @param role: str
        @return: List[UserModel]
        @throws: InternalServerError
        """
        try:
            users_cursor = self.collection.find({"role": role})
            raw_users = list(users_cursor)
            return UserListResponseDTO(users=raw_users)
        except Exception as e:
            logger.error(f"Failed to find users by role {role}: {e}")
            raise InternalServerError(f"Failed to find users by role {role}: {e}")

        
        
        
    def find_user_detail(self, _id: Union[str, ObjectId]) -> UserResponseDTO:
        """Find user's role-specific detail and include role in response"""
        obj_id = self.utils.validate_objectid(_id)
        pipeline = build_user_detail_pipeline(obj_id)
        
        try:
            data = list(self.collection.aggregate(pipeline))
            if not data:
                raise NotFoundError(
                    message="User detail not found",
                    details={"received_value": _id},
                    status_code=404,
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.DATABASE,
                )

            user_doc = data[0]
            user = UserResponseDTO.model_validate(user_doc)

            role_map = self.role_model_map()
            if user.role not in role_map:
                raise NotFoundError(
                    message="Role not found",
                    details={"role": user.role},
                    status_code=404,
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.DATABASE,
                )

            model_cls, collection_name = role_map[user.role]

            role_data_raw = user_doc.get(collection_name)
            if not role_data_raw:
                raise NotFoundError(
                    message=f"{user.role.capitalize()} data not found",
                    details={"received_value": _id},
                    status_code=404,
                    severity=ErrorSeverity.LOW,
                    category=ErrorCategory.DATABASE,
                )

            role_model = model_cls(**role_data_raw)
            role_dump = role_model.model_dump(by_alias=True, exclude_none=True, mode="json")
            cleaned_data = self._convert_objectid_to_str(role_dump)

            return UserResponseDTO(role=user.role, data=cleaned_data)

        except AppBaseException:
            raise
        except Exception as e:
            raise InternalServerError(
                message="Failed to find user detail",
                cause=e,
                details={"received_value": _id},
                status_code=500,
                severity=ErrorSeverity.HIGH,
                category=ErrorCategory.DATABASE,
            )

    def count_users_by_role(self) -> Dict[str, int]:
        try:
            pipeline = [
                {"$group": {"_id": "$role", "count": {"$sum": 1}}}
            ]
            result = self.collection.aggregate(pipeline)
            counts = {role.value: 0 for role in Role}
            for r in result:
                if r["_id"] in counts:
                    counts[r["_id"]] = r["count"]      
            return counts
            
        except Exception as e:
            logger.error(f"Failed to count users by roles: {e}")
            return {} 



    def find_user_growth_stats(self, start_date: str, end_date: str) -> List[UserGrowthStatsResponse]:
        try:
            pipeline = build_user_growth_stats_pipeline(start_date, end_date)
            result = list(self.collection.aggregate(pipeline))
            if not result or ("dailyCounts" not in result[0] and "totalCount" not in result[0]):
                return []

            daily_counts = result[0].get("dailyCounts", [])
            total_count = result[0].get("totalCount", [{}])[0].get("total", 0)

            stats = []
            for entry in daily_counts:
                percent = (entry["count"] / total_count * 100) if total_count > 0 else 0
                stats.append({
                    "date": entry["_id"],
                    "count": entry["count"],
                    "percentage": round(percent, 2)
                })

            return stats
        except AppBaseException:
            raise 
        except Exception as e:
            raise InternalServerError(message="Failed to find user growth stats", cause=e, details={"received_value": start_date, "end_date": end_date}, status_code=500, severity=ErrorSeverity.HIGH, category=ErrorCategory.DATABASE)




    def find_users_growth_stats_by_role_with_comparison(
        self,
        current_start_date: str,
        current_end_date: str,
        previous_start_date: str,
        previous_end_date: str
    ) -> List[UserGrowthStateWithComparisonResponse]:
        """
        Compare user counts by role between two date ranges, calculate growth %.
        """
        current_start_dt, current_end_dt = self._parse_date_range(current_start_date, current_end_date)
        previous_start_dt, previous_end_dt = self._parse_date_range(previous_start_date, previous_end_date)

        def get_role_counts(start_dt: datetime, end_dt: datetime) -> Dict[str, int]:
            pipeline = build_role_counts_pipeline(start_dt, end_dt)
            results = list(self.collection.aggregate(pipeline))
            return {entry["_id"]: entry["count"] for entry in results}

        current_counts = get_role_counts(current_start_dt, current_end_dt)
        previous_counts = get_role_counts(previous_start_dt, previous_end_dt)

        all_roles = set(current_counts.keys()) | set(previous_counts.keys())
        growth_stats = []

        for role in all_roles:
            current = current_counts.get(role, 0)
            previous = previous_counts.get(role, 0)

            if previous == 0:
                growth = 100.0 * current if current > 0 else 0.0
            else:
                growth = ((current - previous) / previous) * 100

            growth_stats.append(UserGrowthStateWithComparisonResponse(role=role, previous=previous, current=current, growth_percentage=round(growth, 2)))

        return growth_stats




def get_user_repository(db: Database) -> UserRepositoryImpl:
    return UserRepositoryImpl(UserRepositoryConfig(db))