from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.shared.time_utils import utc_now


class FinalizePayrollRunUseCase:
    def __init__(self, *, payroll_run_repository, audit_log_repository=None) -> None:
        self.payroll_run_repository = payroll_run_repository
        self.audit_log_repository = audit_log_repository

    def execute(self, *, payroll_run_id, actor_id):
        run = self.payroll_run_repository.find_by_id(payroll_run_id)
        run.finalize(actor_id=actor_id)
        saved = self.payroll_run_repository.save(run)
        self._write_audit_log(
            action="payroll_finalized",
            actor_id=actor_id,
            entity_id=saved.id,
            details={
                "month": saved.month,
                "status": str(saved.status),
            },
        )
        return saved

    def _write_audit_log(self, *, action: str, actor_id, entity_id, details: dict) -> None:
        if not self.audit_log_repository:
            return

        audit_log = AuditLog(
            id=None,
            entity_type="payroll_run",
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            action_at=utc_now(),
            details=details,
        )
        self.audit_log_repository.save(audit_log)
