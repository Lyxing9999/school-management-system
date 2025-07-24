from flask import Blueprint # type: ignore

student_bp = Blueprint('student', __name__)

from . import routes


