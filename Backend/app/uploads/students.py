import os
from flask import Blueprint, request, jsonify, send_from_directory, request
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload_bp", __name__)

# === Upload folder setup ===
UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), "files")
os.makedirs(UPLOAD_ROOT, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# === Helper: Save uploaded file ===
def save_file(file, entity_type: str, entity_id: str):
    if not file or not allowed_file(file.filename):
        raise ValueError("Invalid or missing file")

    folder = os.path.join(UPLOAD_ROOT, entity_type)
    os.makedirs(folder, exist_ok=True)

    ext = os.path.splitext(file.filename)[1]
    filename = f"{entity_id}{ext}"
    filepath = os.path.join(folder, filename)
    file.save(filepath)

    # Return full URL so frontend can access it
    return f"{request.host_url}uploads/{entity_type}/{filename}"


# === Helper: Delete old file ===
def delete_file(file_url: str):
    if not file_url:
        return

    try:
        filename = os.path.basename(file_url)
        folder = file_url.split("/")[2]  # /uploads/students/photo.jpg → students
        filepath = os.path.join(UPLOAD_ROOT, folder, filename)

        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        raise e


# === Serve uploaded files (GET /uploads/<entity>/<filename>) ===
@upload_bp.route("/<entity>/<filename>")
def serve_file(entity, filename):
    folder_path = os.path.join(UPLOAD_ROOT, entity)
    file_path = os.path.join(folder_path, filename)

    return send_from_directory(folder_path, filename)

# === Upload or Update Student Photo (PATCH /api/uploads/student/<student_id>) ===
# === Upload or Update Student Photo ===
@upload_bp.route("/student/<student_id>", methods=["PATCH"])
def upload_student_photo(student_id):
    try:
        file = request.files.get("photo")
        if not file:
            return jsonify({"success": False, "message": "No file uploaded"}), 400

        # Optional: delete old photo if exists
        old_photo_url = request.form.get("old_photo_url")
        if old_photo_url:
            delete_file(old_photo_url)

        # Save new photo
        photo_url = save_file(file, "students", student_id)
        return jsonify({
            "success": True,
            "message": "Photo uploaded successfully",
            "photo_url": photo_url
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500