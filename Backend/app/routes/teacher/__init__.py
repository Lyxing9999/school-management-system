from flask import Blueprint # type: ignore

teacher_bp = Blueprint('teacher', __name__)

from . import routes


