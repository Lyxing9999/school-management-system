from __future__ import annotations

from app.contexts.hrms.domain.payroll import PayrollRun, Payslip
from app.contexts.hrms.errors.payroll_exceptions import PayrollRunAlreadyExistsException


class GenerateMonthlyPayrollUseCase:
    def __init__(
        self,
        *,
        employee_read_model,
        working_schedule_repository,
        public_holiday_repository,
        attendance_repository,
        overtime_repository,
        leave_repository,
        deduction_rule_repository,
        payroll_run_repository,
        payslip_repository,
        audit_log_repository=None,
        payroll_calculator,
        payroll_calendar_service,
    ) -> None:
        self.employee_read_model = employee_read_model
        self.working_schedule_repository = working_schedule_repository
        self.public_holiday_repository = public_holiday_repository
        self.attendance_repository = attendance_repository
        self.overtime_repository = overtime_repository
        self.leave_repository = leave_repository
        self.deduction_rule_repository = deduction_rule_repository
        self.payroll_run_repository = payroll_run_repository
        self.payslip_repository = payslip_repository
        self.audit_log_repository = audit_log_repository
        self.payroll_calculator = payroll_calculator
        self.payroll_calendar_service = payroll_calendar_service

    def execute(self, *, month: str, generated_by):
        existing = self.payroll_run_repository.find_by_month(month)
        if existing:
            raise PayrollRunAlreadyExistsException(month)

        employees, _ = self.employee_read_model.get_page(
            page=1,
            page_size=5000,
            q="",
            show_deleted="active",
        )

        active_employees = [
            e for e in employees
            if str(e.get("status") or "").strip().lower() == "active"
        ]

        month_start, month_end = self.payroll_calendar_service.month_range(month)

        public_holidays = self.public_holiday_repository.list_by_date_range(
            start_date=month_start,
            end_date=month_end,
        )

        deduction_rules, _ = self.deduction_rule_repository.list_rules(
            page=1,
            page_size=500,
            include_deleted=False,
            deleted_only=False,
            is_active=True,
        )

        run = self.payroll_run_repository.save(
            PayrollRun(
                month=month,
                generated_by=generated_by,
            )
        )

        created_payslips = []
        skipped_employees = []

        for employee in active_employees:
            employee_id = employee["_id"]
            basic_salary = float(employee.get("basic_salary") or 0)

            schedule_id = employee.get("schedule_id")
            if not schedule_id:
                skipped_employees.append({
                    "employee_id": str(employee_id),
                    "reason": "missing_schedule_id",
                })
                continue

            schedule = self.working_schedule_repository.find_by_id(schedule_id)
            if not schedule:
                skipped_employees.append({
                    "employee_id": str(employee_id),
                    "reason": "working_schedule_not_found",
                    "schedule_id": str(schedule_id),
                })
                continue

            calendar_info = self.payroll_calendar_service.count_expected_working_days(
                month=month,
                employee=employee,
                working_schedule=schedule,
                public_holidays=public_holidays,
            )

            expected_working_days = int(calendar_info["expected_working_days"])
            paid_holiday_days = int(calendar_info["paid_holiday_days"])

            if expected_working_days <= 0:
                skipped_employees.append({
                    "employee_id": str(employee_id),
                    "reason": "expected_working_days_is_zero",
                })
                continue

            attendances = self.attendance_repository.list_by_employee_and_month(
                employee_id=employee_id,
                month=month,
            )

            overtime_requests = self.overtime_repository.list_approved_by_employee_and_month(
                employee_id=employee_id,
                month=month,
            )

            approved_leaves = self.leave_repository.list_approved_by_employee_and_month(
                employee_id=employee_id,
                month=month,
            )

            unpaid_leave_days = self._count_unpaid_leave_days_in_month(
                approved_leaves=approved_leaves,
                month_start=month_start,
                month_end=month_end,
            )

            calculator = self.payroll_calculator(
                expected_working_days=expected_working_days
            )

            payroll_result = calculator.calculate_net_salary(
                basic_salary=basic_salary,
                attendances=attendances,
                overtime_requests=overtime_requests,
                deduction_rules=deduction_rules,
                unpaid_leave_days=unpaid_leave_days,
            )

            payslip = Payslip(
                payroll_run_id=run.id,
                employee_id=employee_id,
                month=month,
                base_salary=payroll_result["base_salary"],
                payable_working_days=expected_working_days,
                paid_holiday_days=paid_holiday_days,
                unpaid_leave_days=unpaid_leave_days,
                total_ot_hours=payroll_result["total_ot_hours"],
                ot_payment=payroll_result["ot_payment"],
                total_deductions=payroll_result["total_deductions"],
                net_salary=payroll_result["net_salary"],
                attendance_deductions=payroll_result["attendance_deductions"],
                unpaid_leave_deduction=payroll_result["unpaid_leave_deduction"],
                absent_deduction=payroll_result["absent_deduction"],
                late_deduction=payroll_result["late_deduction"],
                early_leave_deduction=payroll_result["early_leave_deduction"],
                wrong_location_deduction=payroll_result["wrong_location_deduction"],
            )
            created_payslips.append(self.payslip_repository.save(payslip))

        return {
            "payroll_run": run,
            "payslips": created_payslips,
            "meta": {
                "employee_count": len(active_employees),
                "generated_count": len(created_payslips),
                "skipped_employees": skipped_employees,
            },
        }

    def _count_unpaid_leave_days_in_month(
        self,
        *,
        approved_leaves: list,
        month_start,
        month_end,
    ) -> int:
        total = 0

        month_start = self.payroll_calendar_service._as_date(month_start)
        month_end = self.payroll_calendar_service._as_date(month_end)

        for leave in approved_leaves:
            if bool(leave.is_paid):
                continue

            leave_start = self.payroll_calendar_service._as_date(leave.start_date)
            leave_end = self.payroll_calendar_service._as_date(leave.end_date)

            overlap_start = max(leave_start, month_start)
            overlap_end = min(leave_end, month_end)

            if overlap_end < overlap_start:
                continue

            total += (overlap_end - overlap_start).days + 1

        return total