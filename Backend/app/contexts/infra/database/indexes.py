from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

IndexKeys = List[Tuple[str, int]]


def _keys_equal(existing_key: Any, wanted_keys: IndexKeys) -> bool:
    """
    Mongo returns index keys as SON (ordered dict). We normalize both sides to
    list[(k,v)] and compare order-sensitive.
    """
    try:
        existing_items = list(existing_key.items())  # SON -> list[(k,v)]
    except Exception:
        return False
    return existing_items == list(wanted_keys)


def _index_effectively_same(
    idx: Dict[str, Any],
    *,
    keys: IndexKeys,
    unique: bool,
    partial: Optional[Dict[str, Any]],
    ttl: Optional[int],
    sparse: Optional[bool],
) -> bool:
    if not _keys_equal(idx.get("key"), keys):
        return False

    if bool(idx.get("unique", False)) != bool(unique):
        return False

    # partialFilterExpression: absent vs None are different; normalize to None if missing
    idx_partial = idx.get("partialFilterExpression", None)
    if idx_partial != partial:
        return False

    # sparse: absent treated as False
    if sparse is not None and bool(idx.get("sparse", False)) != bool(sparse):
        return False

    # TTL index: must match expireAfterSeconds if we asked for TTL
    if ttl is not None and idx.get("expireAfterSeconds") != ttl:
        return False

    return True


def recreate_index(
    col: Collection,
    keys: IndexKeys,
    *,
    name: str,
    unique: bool = False,
    partialFilterExpression: Optional[Dict[str, Any]] = None,
    expireAfterSeconds: Optional[int] = None,
    sparse: Optional[bool] = None,
    background: bool = True,
) -> str:
    """
    DEV/MIGRATION behavior:
    - If same keys/options exist with different name -> drop old name, create desired name.
    - If same name exists with different keys/options -> drop by name, create desired config.
    - Otherwise create if missing.

    IMPORTANT: Does NOT send null options (partialFilterExpression/expireAfterSeconds).
    """
    existing = list(col.list_indexes())

    # 1) If same name exists but config differs -> drop by name
    for idx in existing:
        if idx.get("name") == name and name != "_id_":
            if not _index_effectively_same(
                idx,
                keys=keys,
                unique=unique,
                partial=partialFilterExpression,
                ttl=expireAfterSeconds,
                sparse=sparse,
            ):
                col.drop_index(name)
            break

    existing = list(col.list_indexes())

    # 2) If same keys/options exist under a different name -> drop that index
    for idx in existing:
        idx_name = idx.get("name")
        if idx_name in (None, "_id_", name):
            continue

        if _index_effectively_same(
            idx,
            keys=keys,
            unique=unique,
            partial=partialFilterExpression,
            ttl=expireAfterSeconds,
            sparse=sparse,
        ):
            col.drop_index(idx_name)
            break

    # 3) Create index with ONLY valid options
    kwargs: Dict[str, Any] = {
        "name": name,
        "unique": unique,
        "background": background,
    }
    if partialFilterExpression is not None:
        kwargs["partialFilterExpression"] = partialFilterExpression
    if expireAfterSeconds is not None:
        kwargs["expireAfterSeconds"] = expireAfterSeconds
    if sparse is not None:
        kwargs["sparse"] = sparse

    col.create_index(keys, **kwargs)
    return name


def ensure_indexes(db: Database) -> None:
    # =========================
    # STAFF
    # =========================
    recreate_index(
        db.staff,
        [("user_id", ASCENDING), ("lifecycle.deleted_at", ASCENDING)],
        name="idx_staff_user_id_deleted_at",
    )
    recreate_index(
        db.staff,
        [("user_id", ASCENDING)],
        name="uq_staff_user_id_active_only",
        unique=True,
        partialFilterExpression={"lifecycle.deleted_at": None},
    )

    # =========================
    # REFRESH TOKENS
    # =========================
    recreate_index(
        db.refresh_tokens,
        [("token_hash", ASCENDING)],
        name="uq_refresh_token_hash",
        unique=True,
    )
    recreate_index(
        db.refresh_tokens,
        [("expires_at", ASCENDING)],
        name="idx_refresh_auto_delete_expired",
        expireAfterSeconds=0,
    )

    # =========================
    # CLASSES & STUDENTS
    # =========================
    recreate_index(
        db.classes,
        [("homeroom_teacher_id", ASCENDING), ("lifecycle.deleted_at", ASCENDING)],
        name="idx_classes_teacher_deleted_at",
    )
    recreate_index(
        db.students,
        [("current_class_id", ASCENDING)],
        name="idx_students_current_class_id",
    )

    # =========================
    # SCHEDULES
    # =========================
    recreate_index(
        db.schedules,
        [
            ("class_id", ASCENDING),
            ("lifecycle.deleted_at", ASCENDING),
            ("day_of_week", ASCENDING),
            ("start_time", ASCENDING),
        ],
        name="idx_schedules_class_overlap",
    )
    recreate_index(
        db.schedules,
        [
            ("teacher_id", ASCENDING),
            ("lifecycle.deleted_at", ASCENDING),
            ("day_of_week", ASCENDING),
            ("start_time", ASCENDING),
        ],
        name="idx_schedules_teacher_overlap",
    )

    # =========================
    # IAM
    # =========================
    recreate_index(
        db.iam,
        [("email", ASCENDING)],
        name="uq_iam_email",
        unique=True,
    )
    recreate_index(
        db.iam,
        [("username", ASCENDING)],
        name="uq_iam_username",
        unique=True,
        sparse=True,  # keep only if you really want sparse usernames
    )

    # =========================
    # NOTIFICATIONS
    # =========================
    recreate_index(
        db.notifications,
        [("user_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_notif_user_created_desc",
    )
    recreate_index(
        db.notifications,
        [("user_id", ASCENDING), ("read_at", ASCENDING), ("created_at", DESCENDING)],
        name="idx_notif_user_read_created_desc",
    )
    recreate_index(
        db.notifications,
        [("user_id", ASCENDING), ("type", ASCENDING), ("created_at", DESCENDING)],
        name="idx_notif_user_type_created_desc",
    )
    recreate_index(
        db.notifications,
        [
            ("user_id", ASCENDING),
            ("type", ASCENDING),
            ("read_at", ASCENDING),
            ("created_at", DESCENDING),
        ],
        name="idx_notif_user_type_read_created_desc",
    )

    # =========================
    # SUBJECTS
    # =========================
    recreate_index(
        db.subjects,
        [("code", ASCENDING)],
        name="uq_subject_code_active_only",
        unique=True,
        partialFilterExpression={"lifecycle.deleted_at": None},
    )

    # =========================
    # ATTENDANCE
    # =========================
    recreate_index(
        db.attendance,
        [
            ("class_id", ASCENDING),
            ("record_date", ASCENDING),
            ("lifecycle.deleted_at", ASCENDING),
        ],
        name="idx_attendance_class_record_deleted_at",
    )

    # =========================
    # TEACHER SUBJECT ASSIGNMENTS
    # =========================
    # Your previous unique index: (teacher_id, deleted_at) for active rows
    # was WRONG because it enforces only 1 active assignment per teacher.

    # Query index: list assignments by teacher (active + deleted)
    recreate_index(
        db.teacher_subject_assignments,
        [("teacher_id", ASCENDING), ("lifecycle.deleted_at", ASCENDING)],
        name="idx_tsa_teacher_deleted_at",
        unique=False,
    )

    # Query index: list assignments by class + subject (active + deleted)
    recreate_index(
        db.teacher_subject_assignments,
        [("class_id", ASCENDING), ("subject_id", ASCENDING), ("lifecycle.deleted_at", ASCENDING)],
        name="idx_tsa_class_subject_deleted_at",
        unique=False,
    )

    # Unique rule (recommended): no duplicate ACTIVE assignment for same teacher+class+subject
    recreate_index(
        db.teacher_subject_assignments,
        [("teacher_id", ASCENDING), ("class_id", ASCENDING), ("subject_id", ASCENDING)],
        name="uq_tsa_teacher_class_subject_active",
        unique=True,
        partialFilterExpression={"lifecycle.deleted_at": None},
    )

    # IMPORTANT: Do NOT create this anymore (it causes DuplicateKeyError)
    # recreate_index(
    #     db.teacher_subject_assignments,
    #     [("teacher_id", ASCENDING), ("lifecycle.deleted_at", ASCENDING)],
    #     name="uniq_teacher_created_at",
    #     unique=True,
    #     partialFilterExpression={"lifecycle.deleted_at": None},
    # )