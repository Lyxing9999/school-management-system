from __future__ import annotations

from enum import Enum
from typing import Any
from bson import ObjectId

from app.contexts.shared.lifecycle.domain import Lifecycle, now_utc
from app.contexts.hrms.domain.attendance import AttendanceStatus
from app.contexts.hrms.domain.overtime import OvertimeRequest
from app.contexts.hrms.domain.deduction_rule import DeductionType
from app.contexts.hrms.errors.payroll_exceptions import (
    PayrollExpectedWorkingDaysInvalidException,
    PayrollFinalizeStateInvalidException,
    PayrollMarkPaidStateInvalidException,
    PayrollMonthRequiredException,
    PayslipMonthRequiredException,
)


class PayrollRunStatus(str, Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"
    PAID = "paid"


class PayslipStatus(str, Enum):
    GENERATED = "generated"
    PAID = "paid"


class PayrollRun:
    @staticmethod
    def _normalize_status(value) -> PayrollRunStatus:
        if isinstance(value, PayrollRunStatus):
            return value
        return PayrollRunStatus(str(value).strip().lower())

    def __init__(
        self,
        *,
        month: str,
        generated_by: ObjectId,
        id: ObjectId | None = None,
        status: PayrollRunStatus | str = PayrollRunStatus.DRAFT,
        lifecycle: Lifecycle | None = None,
    ) -> None:
        self.id = id or ObjectId()
        self.month = (month or "").strip()
        self.generated_by = generated_by
        self.status = self._normalize_status(status)
        self.lifecycle = lifecycle or Lifecycle()

        if not self.month:
            raise PayrollMonthRequiredException()

    def finalize(self, *, actor_id: ObjectId) -> None:
        if self.status != PayrollRunStatus.DRAFT:
            raise PayrollFinalizeStateInvalidException(
                str(self.id),
                str(self.status),
            )
        self.status = PayrollRunStatus.FINALIZED
        self.lifecycle.touch(now_utc())

    def mark_paid(self, *, actor_id: ObjectId) -> None:
        if self.status != PayrollRunStatus.FINALIZED:
            raise PayrollMarkPaidStateInvalidException(
                str(self.id),
                str(self.status),
            )
        self.status = PayrollRunStatus.PAID
        self.lifecycle.touch(now_utc())

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()

    def soft_delete(self, *, actor_id: ObjectId | str) -> None:
        self.lifecycle.soft_delete(actor_id=str(actor_id))


class Payslip:
    @staticmethod
    def _normalize_status(value) -> PayslipStatus:
        if isinstance(value, PayslipStatus):
            return value
        return PayslipStatus(str(value).strip().lower())

    def __init__(
        self,
        *,
        payroll_run_id: ObjectId,
        employee_id: ObjectId,
        month: str,
        base_salary: float,
        payable_working_days: int,
        paid_holiday_days: int,
        unpaid_leave_days: int,
        total_ot_hours: float,
        ot_payment: float,
        total_deductions: float,
        net_salary: float,
        id: ObjectId | None = None,
        status: PayslipStatus | str = PayslipStatus.GENERATED,
        lifecycle: Lifecycle | None = None,
        attendance_deductions: float = 0.0,
        unpaid_leave_deduction: float = 0.0,
        absent_deduction: float = 0.0,
        late_deduction: float = 0.0,
        early_leave_deduction: float = 0.0,
        wrong_location_deduction: float = 0.0,
    ) -> None:
        self.id = id or ObjectId()
        self.payroll_run_id = payroll_run_id
        self.employee_id = employee_id
        self.month = (month or "").strip()
        self.base_salary = float(base_salary)
        self.payable_working_days = int(payable_working_days)
        self.paid_holiday_days = int(paid_holiday_days)
        self.unpaid_leave_days = int(unpaid_leave_days)
        self.total_ot_hours = float(total_ot_hours)
        self.ot_payment = float(ot_payment)
        self.total_deductions = float(total_deductions)
        self.net_salary = float(net_salary)

        self.attendance_deductions = float(attendance_deductions)
        self.unpaid_leave_deduction = float(unpaid_leave_deduction)
        self.absent_deduction = float(absent_deduction)
        self.late_deduction = float(late_deduction)
        self.early_leave_deduction = float(early_leave_deduction)
        self.wrong_location_deduction = float(wrong_location_deduction)

        self.status = self._normalize_status(status)
        self.lifecycle = lifecycle or Lifecycle()

        if not self.month:
            raise PayslipMonthRequiredException()

    def mark_paid(self, *, actor_id: ObjectId) -> None:
        self.status = PayslipStatus.PAID
        self.lifecycle.touch(now_utc())

    def is_deleted(self) -> bool:
        return self.lifecycle.is_deleted()


class PayrollCalculator:
    def __init__(self, *, expected_working_days: int) -> None:
        if expected_working_days <= 0:
            raise PayrollExpectedWorkingDaysInvalidException(expected_working_days)
        self.expected_working_days = expected_working_days

    @staticmethod
    def _enum_value(value: Any) -> str:
        if value is None:
            return ""
        return value.value if hasattr(value, "value") else str(value)

    def daily_salary(self, basic_salary: float) -> float:
        return float(basic_salary) / float(self.expected_working_days)

    def _active_rules_for_type(
        self,
        *,
        deduction_rules: list,
        type_value: str,
    ) -> list:
        result = []
        for rule in deduction_rules:
            rule_type = self._enum_value(getattr(rule, "type", ""))
            is_active = bool(getattr(rule, "is_active", False))
            is_deleted = bool(rule.is_deleted()) if hasattr(rule, "is_deleted") else False

            if is_active and not is_deleted and rule_type == type_value:
                result.append(rule)

        return sorted(result, key=lambda r: int(getattr(r, "min_minutes", 0) or 0))

    def calculate_minutes_based_deduction(
        self,
        *,
        daily_salary: float,
        minutes: int,
        deduction_rules: list,
        type_value: str,
    ) -> tuple[float, object | None]:
        if minutes <= 0:
            return 0.0, None

        active_rules = self._active_rules_for_type(
            deduction_rules=deduction_rules,
            type_value=type_value,
        )

        for rule in active_rules:
            if rule.applies_to(minutes):
                return float(rule.calculate_deduction(daily_salary)), rule

        return 0.0, None

    def calculate_attendance_deductions(
        self,
        *,
        attendances: list,
        basic_salary: float,
        deduction_rules: list,
    ) -> dict:
        daily_salary = self.daily_salary(basic_salary)

        absent_deduction = 0.0
        late_deduction = 0.0
        early_leave_deduction = 0.0
        wrong_location_deduction = 0.0
        details: list[dict] = []

        for attendance in attendances:
            status = self._enum_value(getattr(attendance, "status", ""))
            location_review_status = self._enum_value(
                getattr(attendance, "location_review_status", "")
            )

            late_minutes = int(getattr(attendance, "late_minutes", 0) or 0)
            early_leave_minutes = int(getattr(attendance, "early_leave_minutes", 0) or 0)

            attendance_info = {
                "attendance_id": str(getattr(attendance, "id", "")),
                "status": status,
                "late_minutes": late_minutes,
                "early_leave_minutes": early_leave_minutes,
                "location_review_status": location_review_status,
                "absent_deduction": 0.0,
                "late_deduction": 0.0,
                "early_leave_deduction": 0.0,
                "wrong_location_deduction": 0.0,
            }

            if status == AttendanceStatus.HOLIDAY_OFF.value:
                details.append(attendance_info)
                continue

            if status == AttendanceStatus.WEEKEND_OFF.value:
                details.append(attendance_info)
                continue

            if status == AttendanceStatus.ABSENT.value:
                absent_deduction += daily_salary
                attendance_info["absent_deduction"] = daily_salary
                details.append(attendance_info)
                continue

            if (
                location_review_status == "rejected"
                or status == AttendanceStatus.WRONG_LOCATION_REJECTED.value
            ):
                wrong_location_deduction += daily_salary
                attendance_info["wrong_location_deduction"] = daily_salary
                details.append(attendance_info)
                continue

            late_amount, late_rule = self.calculate_minutes_based_deduction(
                daily_salary=daily_salary,
                minutes=late_minutes,
                deduction_rules=deduction_rules,
                type_value=DeductionType.LATE.value,
            )
            late_deduction += late_amount
            attendance_info["late_deduction"] = late_amount
            if late_rule:
                attendance_info["late_rule"] = {
                    "id": str(getattr(late_rule, "id", "")),
                    "min_minutes": getattr(late_rule, "min_minutes", 0),
                    "max_minutes": getattr(late_rule, "max_minutes", None),
                    "deduction_value": getattr(late_rule, "deduction_value", 0),
                    "deduction_mode": str(getattr(late_rule, "deduction_mode", "")),
                }

            early_leave_amount, early_leave_rule = self.calculate_minutes_based_deduction(
                daily_salary=daily_salary,
                minutes=early_leave_minutes,
                deduction_rules=deduction_rules,
                type_value=DeductionType.EARLY_LEAVE.value,
            )
            early_leave_deduction += early_leave_amount
            attendance_info["early_leave_deduction"] = early_leave_amount
            if early_leave_rule:
                attendance_info["early_leave_rule"] = {
                    "id": str(getattr(early_leave_rule, "id", "")),
                    "min_minutes": getattr(early_leave_rule, "min_minutes", 0),
                    "max_minutes": getattr(early_leave_rule, "max_minutes", None),
                    "deduction_value": getattr(early_leave_rule, "deduction_value", 0),
                    "deduction_mode": str(getattr(early_leave_rule, "deduction_mode", "")),
                }

            details.append(attendance_info)

        total = absent_deduction + late_deduction + early_leave_deduction + wrong_location_deduction

        return {
            "daily_salary": daily_salary,
            "absent_deduction": absent_deduction,
            "late_deduction": late_deduction,
            "early_leave_deduction": early_leave_deduction,
            "wrong_location_deduction": wrong_location_deduction,
            "total": total,
            "details": details,
        }

    def calculate_unpaid_leave_deduction(
        self,
        *,
        basic_salary: float,
        unpaid_leave_days: int,
    ) -> float:
        if unpaid_leave_days <= 0:
            return 0.0
        return self.daily_salary(basic_salary) * float(unpaid_leave_days)

    def calculate_ot_payment(
        self,
        *,
        overtime_requests: list[OvertimeRequest],
    ) -> tuple[float, float]:
        total_hours = 0.0
        total_payment = 0.0

        for ot in overtime_requests:
            if not ot.is_payable():
                continue

            total_hours += float(ot.approved_hours or 0)
            total_payment += float(ot.calculated_payment or 0)

        return total_hours, total_payment

    def calculate_net_salary(
        self,
        *,
        basic_salary: float,
        attendances: list,
        overtime_requests: list[OvertimeRequest],
        deduction_rules: list,
        unpaid_leave_days: int = 0,
    ) -> dict:
        attendance_result = self.calculate_attendance_deductions(
            attendances=attendances,
            basic_salary=basic_salary,
            deduction_rules=deduction_rules,
        )

        unpaid_leave_deduction = self.calculate_unpaid_leave_deduction(
            basic_salary=basic_salary,
            unpaid_leave_days=unpaid_leave_days,
        )

        total_deductions = float(attendance_result["total"]) + float(unpaid_leave_deduction)

        total_ot_hours, ot_payment = self.calculate_ot_payment(
            overtime_requests=overtime_requests
        )

        net_salary = float(basic_salary) + float(ot_payment) - float(total_deductions)

        return {
            "base_salary": float(basic_salary),
            "daily_salary": float(attendance_result["daily_salary"]),
            "total_ot_hours": float(total_ot_hours),
            "ot_payment": float(ot_payment),
            "attendance_deductions": float(attendance_result["total"]),
            "absent_deduction": float(attendance_result["absent_deduction"]),
            "late_deduction": float(attendance_result["late_deduction"]),
            "early_leave_deduction": float(attendance_result["early_leave_deduction"]),
            "wrong_location_deduction": float(attendance_result["wrong_location_deduction"]),
            "unpaid_leave_deduction": float(unpaid_leave_deduction),
            "total_deductions": float(total_deductions),
            "net_salary": float(net_salary),
            "attendance_breakdown": attendance_result["details"],
        }