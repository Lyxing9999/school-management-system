from flask import jsonify, Blueprint
from app.routes.student import student_bp
from app.services.student_service import MongoStudentService
from app.auth.jwt_utils import role_required
from app.enums.roles import Role
from app.utils.response_utils import Response  # type: ignore
from app.utils.objectid import ObjectId # type: ignore
from app.utils.console import console
from flask import jsonify , g # type: ignore
from app.database.db import get_db # type: ignore
from app.models.classes  import ClassesModel  


student_bp = Blueprint('student', __name__)







