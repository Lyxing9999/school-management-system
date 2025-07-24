from flask import Blueprint # type: ignore

admin_bp = Blueprint('admin', __name__)

from . import routes


