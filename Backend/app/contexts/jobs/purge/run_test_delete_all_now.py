from __future__ import annotations

from app.contexts.infra.database.job_db import get_job_db
from app.contexts.jobs.purge.purge_soft_deleted import PurgeCollectionPlan, run_purge_soft_deleted


def run() -> None:
    db = get_job_db()

    collections = [
        PurgeCollectionPlan("attendance"),
        PurgeCollectionPlan("grades"),
        PurgeCollectionPlan("schedules"),
        PurgeCollectionPlan("teacher_subject_assignments"),
        PurgeCollectionPlan("classes"),
        PurgeCollectionPlan("subjects"),
        PurgeCollectionPlan("students"),
    ]

    result = run_purge_soft_deleted(
        db,
        retention_days=0,
        batch_size=500,
        dry_run=False,
        collections=collections,
        write_audit=True,
        actor_id="manual_purge_now",
    )

if __name__ == "__main__":
    run()