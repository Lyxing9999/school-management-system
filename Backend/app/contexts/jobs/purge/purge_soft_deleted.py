from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence

from pymongo.collection import Collection
from pymongo.database import Database

from app.contexts.shared.lifecycle.filters import FIELDS


@dataclass(frozen=True)
class PurgeCollectionPlan:
    name: str
    query_extra: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class PurgeStats:
    collection: str
    eligible: int
    deleted: int


@dataclass(frozen=True)
class PurgeRunResult:
    cutoff: datetime
    dry_run: bool
    retention_days: int
    batch_size: int
    stats: List[PurgeStats]
    errors: List[str]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _cutoff_dt(retention_days: int, now: Optional[datetime] = None) -> datetime:
    base = now or _utc_now()
    return base - timedelta(days=int(retention_days))


def _deleted_before_cutoff_query(
    cutoff: datetime,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    q: Dict[str, Any] = {
        FIELDS.k(FIELDS.deleted_at): {"$exists": True, "$ne": None, "$lte": cutoff}
    }
    if extra:
        q.update(extra)
    return q


def _find_ids_batch(col: Collection, query: Dict[str, Any], batch_size: int) -> List[Any]:
    cur = col.find(query, {"_id": 1}).sort([("_id", 1)]).limit(int(batch_size))
    return [d["_id"] for d in cur if d.get("_id") is not None]


def _delete_ids_batch(col: Collection, ids: Sequence[Any]) -> int:
    if not ids:
        return 0
    res = col.delete_many({"_id": {"$in": list(ids)}})
    return int(res.deleted_count or 0)


def _count_eligible(col: Collection, query: Dict[str, Any]) -> int:
    return int(col.count_documents(query))


def _dedupe_plans(plans: List[PurgeCollectionPlan]) -> List[PurgeCollectionPlan]:
    seen: set[str] = set()
    out: List[PurgeCollectionPlan] = []
    for p in plans:
        if p.name in seen:
            continue
        seen.add(p.name)
        out.append(p)
    return out


def run_purge_soft_deleted(
    db: Database,
    *,
    retention_days: int,
    batch_size: int = 500,
    dry_run: bool = True,
    collections: Optional[Iterable[PurgeCollectionPlan]] = None,
    write_audit: bool = True,
    actor_id: Optional[str] = None,
    cutoff_override: Optional[datetime] = None,
    max_batches_per_collection: int = 10_000,
) -> PurgeRunResult:
    now = _utc_now()
    cutoff = cutoff_override if cutoff_override is not None else _cutoff_dt(retention_days=retention_days, now=now)

    default_collections: List[PurgeCollectionPlan] = [
        PurgeCollectionPlan("attendance"),
        PurgeCollectionPlan("grades"),
        PurgeCollectionPlan("schedules"),
        PurgeCollectionPlan("teacher_subject_assignments"),
        PurgeCollectionPlan("classes"),
        PurgeCollectionPlan("subjects"),
        PurgeCollectionPlan("students"),
        PurgeCollectionPlan("iam"),
        PurgeCollectionPlan("staff"),
    ]

    plans = list(collections) if collections is not None else default_collections
    plans = _dedupe_plans(plans)

    stats: List[PurgeStats] = []
    errors: List[str] = []

    for plan in plans:
        try:
            col = db[plan.name]
            query = _deleted_before_cutoff_query(cutoff, plan.query_extra)

            eligible = _count_eligible(col, query)
            deleted_total = 0

            if not dry_run and eligible > 0:
                batches = 0
                while True:
                    if batches >= int(max_batches_per_collection):
                        errors.append(f"{plan.name}: max_batches_per_collection reached")
                        break
                    ids = _find_ids_batch(col, query, batch_size=batch_size)
                    if not ids:
                        break
                    deleted_total += _delete_ids_batch(col, ids)
                    batches += 1

            stats.append(PurgeStats(collection=plan.name, eligible=eligible, deleted=deleted_total))
        except Exception as e:
            errors.append(f"{plan.name}: {type(e).__name__}: {e}")

    if write_audit:
        try:
            audit_doc: Dict[str, Any] = {
                "created_at": now,
                "cutoff": cutoff,
                "dry_run": bool(dry_run),
                "retention_days": int(retention_days),
                "batch_size": int(batch_size),
                "actor_id": actor_id,
                "stats": [s.__dict__ for s in stats],
                "errors": list(errors),
            }
            db["purge_audit"].insert_one(audit_doc)
        except Exception as e:
            errors.append(f"purge_audit: {type(e).__name__}: {e}")

    return PurgeRunResult(
        cutoff=cutoff,
        dry_run=bool(dry_run),
        retention_days=int(retention_days),
        batch_size=int(batch_size),
        stats=stats,
        errors=errors,
    )


def test_purge_one_minute(db: Database) -> PurgeRunResult:
    col_name = "purge_test_items"
    col = db[col_name]
    col.delete_many({})

    now = _utc_now()
    doc_old = {
        "name": "old_deleted",
        "lifecycle": {
            "deleted_at": now - timedelta(minutes=2),
            "deleted_by": None,
        },
    }
    doc_new = {
        "name": "new_deleted",
        "lifecycle": {
            "deleted_at": now,
            "deleted_by": None,
        },
    }
    col.insert_many([doc_old, doc_new])

    cutoff_1_min = now - timedelta(minutes=1)

    result = run_purge_soft_deleted(
        db,
        retention_days=0,
        batch_size=100,
        dry_run=False,
        collections=[PurgeCollectionPlan(col_name)],
        write_audit=False,
        cutoff_override=cutoff_1_min,
    )

    remaining = list(col.find({}, {"name": 1, "lifecycle.deleted_at": 1}))
    remaining_names = sorted([d.get("name") for d in remaining])

    if remaining_names != ["new_deleted"]:
        raise AssertionError(
            f"Expected only ['new_deleted'] to remain, got {remaining_names}"
        )

    eligible = result.stats[0].eligible if result.stats else None
    deleted = result.stats[0].deleted if result.stats else None
    if eligible != 1 or deleted != 1:
        raise AssertionError(f"Expected eligible=1 and deleted=1, got eligible={eligible}, deleted={deleted}")

    col.drop()
    return result