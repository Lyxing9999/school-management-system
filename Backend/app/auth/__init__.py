from flask import Blueprint  # type: ignore

auth_bp = Blueprint('auth', __name__)

from . import routes