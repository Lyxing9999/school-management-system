from __future__ import annotations

from pymongo.database import Database
from pymongo import ASCENDING, DESCENDING


def ensure_indexes(db: Database) -> None:
    """
    Create MongoDB indexes (idempotent).
    Safe to call at startup; MongoDB will only create if missing.
    """

    # -------------------------
    # STAFF
    # -------------------------
    # Fast resolve staff by IAM user id + not_deleted()
    db.staff.create_index(
        [("user_id", ASCENDING), ("lifecycle.deleted_at", ASCENDING)],
        name="idx_staff_user_id_deleted_at",
        background=True,
    )

    # Optional: listing / sorting staff
    db.staff.create_index(
        [("lifecycle.created_at", DESCENDING)],
        name="idx_staff_created_at_desc",
        background=True,
    )

    # Optional but recommended: prevent multiple ACTIVE staff profiles per user
    # Allows duplicates only if older docs are soft-deleted
    db.staff.create_index(
        [("user_id", ASCENDING)],
        name="uq_staff_user_id_active_only",
        unique=True,
        partialFilterExpression={"lifecycle.deleted_at": None},
        background=True,
    )

    # -------------------------
    # REFRESH TOKENS
    # -------------------------
    # Lookup by token_hash must be fast + unique
    db.refresh_tokens.create_index(
        [("token_hash", ASCENDING)],
        name="uq_refresh_token_hash",
        unique=True,
        background=True,
    )

    # Useful for revocation checks / user sessions / cleanup scans
    db.refresh_tokens.create_index(
        [("user_id", ASCENDING), ("revoked_at", ASCENDING), ("expires_at", ASCENDING)],
        name="idx_refresh_user_revoked_expires",
        background=True,
    )

    # Optional: if you do cleanup jobs like "delete expired"
    db.refresh_tokens.create_index(
        [("expires_at", ASCENDING)],
        name="idx_refresh_expires_at",
        background=True,
    )

    # -------------------------
    # CLASSES / SCHEDULES (teacher references)
    # -------------------------
    db.classes.create_index(
        [("teacher_id", ASCENDING), ("lifecycle.deleted_at", ASCENDING)],
        name="idx_classes_teacher_deleted_at",
        background=True,
    )

    db.schedules.create_index(
        [("teacher_id", ASCENDING), ("lifecycle.deleted_at", ASCENDING)],
        name="idx_schedules_teacher_deleted_at",
        background=True,
    )

    # -------------------------
    # IAM (optional but typically important)
    # -------------------------
    # If you query/filter users by role + not_deleted + sort by lifecycle.created_at:
    db.iam.create_index(
        [("role", ASCENDING), ("lifecycle.deleted_at", ASCENDING), ("lifecycle.created_at", DESCENDING)],
        name="idx_iam_role_deleted_created",
        background=True,
    )

    # Unique identities (adjust field names to your schema)
    db.iam.create_index(
        [("email", ASCENDING)],
        unique=True,
        background=True)

    db.iam.create_index(
        [("username", ASCENDING)],
        unique=True,
        background=True,
        sparse=True)



    db.students.create_index([("current_class_id", 1)], name="idx_students_current_class_id", background=True)
    db.students.create_index([("lifecycle.deleted_at", 1)], name="idx_students_deleted_at", background=True)