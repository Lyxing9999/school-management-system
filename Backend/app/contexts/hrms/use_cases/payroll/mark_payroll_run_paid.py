from __future__ import annotations

from app.contexts.hrms.domain.audit_log import AuditLog
from app.contexts.shared.time_utils import utc_now


class MarkPayrollRunPaidUseCase:
    def __init__(
        self,
        *,
        payroll_run_repository,
        payslip_repository,
        audit_log_repository=None,
        notification_service=None,
    ) -> None:
        self.payroll_run_repository = payroll_run_repository
        self.payslip_repository = payslip_repository
        self.audit_log_repository = audit_log_repository
        self.notification_service = notification_service

    def execute(self, *, payroll_run_id, actor_id):
        run = self.payroll_run_repository.find_by_id(payroll_run_id)
        run.mark_paid(actor_id=actor_id)
        saved_run = self.payroll_run_repository.save(run)

        payslips, _ = self.payslip_repository.list_payslips(
            payroll_run_id=payroll_run_id,
            page=1,
            page_size=5000,
        )
        for payslip in payslips:
            payslip.mark_paid(actor_id=actor_id)
            self.payslip_repository.save(payslip)

        self._write_audit_log(
            action="payroll_marked_paid",
            actor_id=actor_id,
            entity_id=saved_run.id,
            details={
                "month": saved_run.month,
                "status": str(saved_run.status),
                "payslip_count": len(payslips),
            },
        )
        if self.notification_service:
            self.notification_service.notify_payroll_marked_paid(
                payroll_run_id=saved_run.id,
                month=saved_run.month,
                actor_user_id=actor_id,
                employee_ids=[payslip.employee_id for payslip in payslips],
            )

        return saved_run

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
