from __future__ import annotations

from typing import Any, Iterable

from bson import ObjectId
from pymongo.database import Database

from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.notifications.services.notification_service import NotificationService
from app.contexts.shared.model_converter import mongo_converter


class HrmsNotificationType:
    LEAVE_SUBMITTED = "HRMS_LEAVE_SUBMITTED"
    LEAVE_APPROVED = "HRMS_LEAVE_APPROVED"
    LEAVE_REJECTED = "HRMS_LEAVE_REJECTED"
    LEAVE_CANCELLED = "HRMS_LEAVE_CANCELLED"

    OVERTIME_SUBMITTED = "HRMS_OVERTIME_SUBMITTED"
    OVERTIME_APPROVED = "HRMS_OVERTIME_APPROVED"
    OVERTIME_REJECTED = "HRMS_OVERTIME_REJECTED"
    OVERTIME_CANCELLED = "HRMS_OVERTIME_CANCELLED"

    PAYROLL_GENERATED = "HRMS_PAYROLL_GENERATED"
    PAYROLL_FINALIZED = "HRMS_PAYROLL_FINALIZED"
    PAYROLL_MARKED_PAID = "HRMS_PAYROLL_MARKED_PAID"
    PAYSLIP_READY = "HRMS_PAYSLIP_READY"

    ATTENDANCE_WRONG_LOCATION_APPROVED = "HRMS_ATTENDANCE_WRONG_LOCATION_APPROVED"
    ATTENDANCE_WRONG_LOCATION_REJECTED = "HRMS_ATTENDANCE_WRONG_LOCATION_REJECTED"
    ATTENDANCE_EARLY_LEAVE_APPROVED = "HRMS_ATTENDANCE_EARLY_LEAVE_APPROVED"
    ATTENDANCE_EARLY_LEAVE_REJECTED = "HRMS_ATTENDANCE_EARLY_LEAVE_REJECTED"


class HrmsNotificationService:
    """
    HRMS-only notification dispatcher.

    This layer keeps emit logic centralized and best-effort:
    notifications must never fail command workflows.
    """

    def __init__(self, *, db: Database, employee_repository) -> None:
        self._notification_service = NotificationService(db)
        self._iam_read_model = IAMReadModel(db)
        self._employee_repository = employee_repository
        self._employee_collection = db["hr_employees"]

    @staticmethod
    def _sid(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        if text.lower() in {"", "null", "none", "undefined"}:
            return None
        return text

    @staticmethod
    def _employee_name(employee: dict | None) -> str | None:
        if not employee:
            return None
        full_name = str(employee.get("full_name") or "").strip()
        if full_name:
            return full_name
        code = str(employee.get("employee_code") or "").strip()
        return code or None

    def _employee_or_none(self, employee_id) -> dict | None:
        try:
            return self._employee_repository.find_by_id(employee_id)
        except Exception:
            return None

    def _employees_by_ids(self, employee_ids: Iterable[Any]) -> dict[str, dict]:
        oids: list[ObjectId] = []
        seen: set[ObjectId] = set()

        for raw in employee_ids:
            oid = mongo_converter.convert_to_object_id(raw)
            if not oid or oid in seen:
                continue
            seen.add(oid)
            oids.append(oid)

        if not oids:
            return {}

        rows = list(
            self._employee_collection.find(
                {"_id": {"$in": oids}},
                {"_id": 1, "full_name": 1, "employee_code": 1, "user_id": 1, "manager_user_id": 1},
            )
        )
        return {str(row.get("_id")): row for row in rows if row.get("_id")}

    def _user_or_none(self, user_id) -> dict | None:
        uid = self._sid(user_id)
        if not uid:
            return None
        try:
            return self._iam_read_model.get_by_id(uid, show_deleted="all")
        except Exception:
            return None

    def _user_name(self, user_id) -> str | None:
        user = self._user_or_none(user_id)
        if not user:
            return None
        username = str(user.get("username") or "").strip()
        if username:
            return username
        email = str(user.get("email") or "").strip()
        return email or None

    def _role_user_ids(self, role: str) -> list[str]:
        try:
            ids = self._iam_read_model.list_active_user_ids_by_role(role)
        except Exception:
            return []
        return [str(uid) for uid in ids if uid]

    def _notify_user(
        self,
        *,
        user_id: str | None,
        role: str,
        type_: str,
        title: str,
        message: str,
        entity_type: str,
        entity_id: str | None,
        data: dict | None = None,
    ) -> None:
        uid = self._sid(user_id)
        if not uid:
            return
        try:
            self._notification_service.create_for_user(
                user_id=uid,
                role=role,
                type=type_,
                title=title,
                message=message,
                entity_type=entity_type,
                entity_id=entity_id,
                data=data or {},
            )
        except Exception:
            # Notification is best-effort; never break business commands.
            return

    def _notify_many(
        self,
        *,
        recipients: Iterable[tuple[str | None, str]],
        type_: str,
        title: str,
        message: str,
        entity_type: str,
        entity_id: str | None,
        data: dict | None = None,
    ) -> None:
        seen: set[str] = set()
        for user_id, role in recipients:
            uid = self._sid(user_id)
            if not uid or uid in seen:
                continue
            seen.add(uid)
            self._notify_user(
                user_id=uid,
                role=role,
                type_=type_,
                title=title,
                message=message,
                entity_type=entity_type,
                entity_id=entity_id,
                data=data,
            )

    def _manager_and_hr_admin_recipients(
        self,
        *,
        employee: dict | None,
        exclude_user_ids: set[str] | None = None,
    ) -> list[tuple[str, str]]:
        excluded = exclude_user_ids or set()
        out: list[tuple[str, str]] = []

        manager_user_id = self._sid(employee.get("manager_user_id")) if employee else None
        if manager_user_id and manager_user_id not in excluded:
            out.append((manager_user_id, "manager"))

        for admin_user_id in self._role_user_ids("hr_admin"):
            if admin_user_id in excluded:
                continue
            out.append((admin_user_id, "hr_admin"))

        return out

    def notify_leave_submitted(
        self,
        *,
        leave_id,
        employee_id,
        leave_type: str | None,
        start_date,
        end_date,
    ) -> None:
        try:
            employee = self._employee_or_none(employee_id)
            employee_name = self._employee_name(employee) or "Employee"

            recipients = self._manager_and_hr_admin_recipients(
                employee=employee,
                exclude_user_ids={self._sid(employee.get("user_id"))} if employee else set(),
            )

            leave_type_label = str(leave_type or "leave").strip() or "leave"
            message = (
                f"{employee_name} submitted {leave_type_label} "
                f"({start_date} to {end_date})."
            )

            self._notify_many(
                recipients=recipients,
                type_=HrmsNotificationType.LEAVE_SUBMITTED,
                title="New leave request",
                message=message,
                entity_type="hrms_leave_request",
                entity_id=self._sid(leave_id),
                data={
                    "route": "/hr/leaves/reviews",
                    "leave_id": self._sid(leave_id),
                    "employee_id": self._sid(employee_id),
                    "employee_name": employee_name,
                    "leave_type": leave_type_label,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                },
            )
        except Exception:
            return

    def notify_leave_reviewed(
        self,
        *,
        leave_id,
        employee_id,
        approved: bool,
        reviewer_user_id=None,
        comment: str | None = None,
    ) -> None:
        try:
            employee = self._employee_or_none(employee_id)
            employee_user_id = self._sid(employee.get("user_id")) if employee else None
            if not employee_user_id:
                return

            reviewer_name = self._user_name(reviewer_user_id)
            status_text = "approved" if approved else "rejected"
            type_ = (
                HrmsNotificationType.LEAVE_APPROVED
                if approved
                else HrmsNotificationType.LEAVE_REJECTED
            )
            by_part = f" by {reviewer_name}" if reviewer_name else ""
            comment_part = f" Comment: {comment}" if str(comment or "").strip() else ""

            self._notify_user(
                user_id=employee_user_id,
                role="employee",
                type_=type_,
                title=f"Leave request {status_text}",
                message=f"Your leave request was {status_text}{by_part}.{comment_part}",
                entity_type="hrms_leave_request",
                entity_id=self._sid(leave_id),
                data={
                    "route": "/hr/leaves",
                    "leave_id": self._sid(leave_id),
                    "employee_id": self._sid(employee_id),
                    "status": status_text,
                    "comment": comment,
                },
            )
        except Exception:
            return

    def notify_leave_cancelled(
        self,
        *,
        leave_id,
        employee_id,
        actor_user_id=None,
        actor_role: str | None = None,
    ) -> None:
        try:
            employee = self._employee_or_none(employee_id)
            if not employee:
                return

            employee_user_id = self._sid(employee.get("user_id"))
            actor_user_id = self._sid(actor_user_id)
            normalized_role = str(actor_role or "").strip().lower()
            actor_name = self._user_name(actor_user_id)

            if normalized_role == "employee":
                recipients = self._manager_and_hr_admin_recipients(
                    employee=employee,
                    exclude_user_ids={actor_user_id} if actor_user_id else set(),
                )
                self._notify_many(
                    recipients=recipients,
                    type_=HrmsNotificationType.LEAVE_CANCELLED,
                    title="Leave request cancelled",
                    message=(
                        f"{self._employee_name(employee) or 'Employee'} cancelled a leave request."
                    ),
                    entity_type="hrms_leave_request",
                    entity_id=self._sid(leave_id),
                    data={
                        "route": "/hr/leaves/reviews",
                        "leave_id": self._sid(leave_id),
                        "employee_id": self._sid(employee_id),
                        "employee_name": self._employee_name(employee),
                        "cancelled_by_role": normalized_role or None,
                    },
                )
                return

            if employee_user_id and employee_user_id != actor_user_id:
                by_part = f" by {actor_name}" if actor_name else ""
                self._notify_user(
                    user_id=employee_user_id,
                    role="employee",
                    type_=HrmsNotificationType.LEAVE_CANCELLED,
                    title="Leave request cancelled",
                    message=f"Your leave request was cancelled{by_part}.",
                    entity_type="hrms_leave_request",
                    entity_id=self._sid(leave_id),
                    data={
                        "route": "/hr/leaves",
                        "leave_id": self._sid(leave_id),
                        "employee_id": self._sid(employee_id),
                        "cancelled_by_role": normalized_role or None,
                    },
                )
        except Exception:
            return

    def notify_overtime_submitted(
        self,
        *,
        overtime_id,
        employee_id,
        request_date,
    ) -> None:
        try:
            employee = self._employee_or_none(employee_id)
            employee_name = self._employee_name(employee) or "Employee"

            recipients = self._manager_and_hr_admin_recipients(
                employee=employee,
                exclude_user_ids={self._sid(employee.get("user_id"))} if employee else set(),
            )
            self._notify_many(
                recipients=recipients,
                type_=HrmsNotificationType.OVERTIME_SUBMITTED,
                title="New overtime request",
                message=f"{employee_name} submitted overtime for {request_date}.",
                entity_type="hrms_overtime_request",
                entity_id=self._sid(overtime_id),
                data={
                    "route": "/hr/overtime/reviews",
                    "overtime_id": self._sid(overtime_id),
                    "employee_id": self._sid(employee_id),
                    "employee_name": employee_name,
                    "request_date": str(request_date),
                },
            )
        except Exception:
            return

    def notify_overtime_reviewed(
        self,
        *,
        overtime_id,
        employee_id,
        approved: bool,
        reviewer_user_id=None,
        comment: str | None = None,
    ) -> None:
        try:
            employee = self._employee_or_none(employee_id)
            employee_user_id = self._sid(employee.get("user_id")) if employee else None
            if not employee_user_id:
                return

            reviewer_name = self._user_name(reviewer_user_id)
            status_text = "approved" if approved else "rejected"
            type_ = (
                HrmsNotificationType.OVERTIME_APPROVED
                if approved
                else HrmsNotificationType.OVERTIME_REJECTED
            )
            by_part = f" by {reviewer_name}" if reviewer_name else ""
            comment_part = f" Comment: {comment}" if str(comment or "").strip() else ""

            self._notify_user(
                user_id=employee_user_id,
                role="employee",
                type_=type_,
                title=f"Overtime request {status_text}",
                message=f"Your overtime request was {status_text}{by_part}.{comment_part}",
                entity_type="hrms_overtime_request",
                entity_id=self._sid(overtime_id),
                data={
                    "route": "/hr/overtime",
                    "overtime_id": self._sid(overtime_id),
                    "employee_id": self._sid(employee_id),
                    "status": status_text,
                    "comment": comment,
                },
            )
        except Exception:
            return

    def notify_overtime_cancelled(
        self,
        *,
        overtime_id,
        employee_id,
        actor_user_id=None,
        actor_role: str | None = None,
    ) -> None:
        try:
            employee = self._employee_or_none(employee_id)
            if not employee:
                return

            employee_user_id = self._sid(employee.get("user_id"))
            actor_user_id = self._sid(actor_user_id)
            normalized_role = str(actor_role or "").strip().lower()
            actor_name = self._user_name(actor_user_id)

            if normalized_role == "employee":
                recipients = self._manager_and_hr_admin_recipients(
                    employee=employee,
                    exclude_user_ids={actor_user_id} if actor_user_id else set(),
                )
                self._notify_many(
                    recipients=recipients,
                    type_=HrmsNotificationType.OVERTIME_CANCELLED,
                    title="Overtime request cancelled",
                    message=(
                        f"{self._employee_name(employee) or 'Employee'} cancelled an overtime request."
                    ),
                    entity_type="hrms_overtime_request",
                    entity_id=self._sid(overtime_id),
                    data={
                        "route": "/hr/overtime/reviews",
                        "overtime_id": self._sid(overtime_id),
                        "employee_id": self._sid(employee_id),
                        "employee_name": self._employee_name(employee),
                        "cancelled_by_role": normalized_role or None,
                    },
                )
                return

            if employee_user_id and employee_user_id != actor_user_id:
                by_part = f" by {actor_name}" if actor_name else ""
                self._notify_user(
                    user_id=employee_user_id,
                    role="employee",
                    type_=HrmsNotificationType.OVERTIME_CANCELLED,
                    title="Overtime request cancelled",
                    message=f"Your overtime request was cancelled{by_part}.",
                    entity_type="hrms_overtime_request",
                    entity_id=self._sid(overtime_id),
                    data={
                        "route": "/hr/overtime",
                        "overtime_id": self._sid(overtime_id),
                        "employee_id": self._sid(employee_id),
                        "cancelled_by_role": normalized_role or None,
                    },
                )
        except Exception:
            return

    def notify_payroll_generated(
        self,
        *,
        payroll_run_id,
        month: str,
        generated_by_user_id=None,
        generated_count: int = 0,
        employee_count: int = 0,
    ) -> None:
        try:
            actor_user_id = self._sid(generated_by_user_id)
            recipients: list[tuple[str, str]] = []
            for user_id in self._role_user_ids("payroll_manager"):
                if user_id != actor_user_id:
                    recipients.append((user_id, "payroll_manager"))
            for user_id in self._role_user_ids("hr_admin"):
                if user_id != actor_user_id:
                    recipients.append((user_id, "hr_admin"))

            self._notify_many(
                recipients=recipients,
                type_=HrmsNotificationType.PAYROLL_GENERATED,
                title=f"Payroll generated ({month})",
                message=(
                    f"Payroll run generated for {month}. "
                    f"{int(generated_count)} of {int(employee_count)} employees processed."
                ),
                entity_type="hrms_payroll_run",
                entity_id=self._sid(payroll_run_id),
                data={
                    "route": "/hr/payroll/runs",
                    "payroll_run_id": self._sid(payroll_run_id),
                    "month": month,
                    "generated_count": int(generated_count),
                    "employee_count": int(employee_count),
                },
            )
        except Exception:
            return

    def notify_payroll_finalized(
        self,
        *,
        payroll_run_id,
        month: str,
        actor_user_id=None,
    ) -> None:
        try:
            actor_user_id = self._sid(actor_user_id)
            recipients: list[tuple[str, str]] = []
            for user_id in self._role_user_ids("payroll_manager"):
                if user_id != actor_user_id:
                    recipients.append((user_id, "payroll_manager"))
            for user_id in self._role_user_ids("hr_admin"):
                if user_id != actor_user_id:
                    recipients.append((user_id, "hr_admin"))

            self._notify_many(
                recipients=recipients,
                type_=HrmsNotificationType.PAYROLL_FINALIZED,
                title=f"Payroll finalized ({month})",
                message=f"Payroll run for {month} has been finalized.",
                entity_type="hrms_payroll_run",
                entity_id=self._sid(payroll_run_id),
                data={
                    "route": "/hr/payroll/runs",
                    "payroll_run_id": self._sid(payroll_run_id),
                    "month": month,
                },
            )
        except Exception:
            return

    def notify_payroll_marked_paid(
        self,
        *,
        payroll_run_id,
        month: str,
        actor_user_id=None,
        employee_ids: Iterable[Any],
    ) -> None:
        try:
            employee_map = self._employees_by_ids(employee_ids)
            seen_employee_user_ids: set[str] = set()

            for employee in employee_map.values():
                employee_user_id = self._sid(employee.get("user_id"))
                if not employee_user_id or employee_user_id in seen_employee_user_ids:
                    continue
                seen_employee_user_ids.add(employee_user_id)
                self._notify_user(
                    user_id=employee_user_id,
                    role="employee",
                    type_=HrmsNotificationType.PAYSLIP_READY,
                    title=f"Payroll paid ({month})",
                    message=f"Your payroll for {month} has been marked paid.",
                    entity_type="hrms_payroll_run",
                    entity_id=self._sid(payroll_run_id),
                    data={
                        "route": "/hr/payroll/payslips",
                        "payroll_run_id": self._sid(payroll_run_id),
                        "month": month,
                    },
                )

            actor_user_id = self._sid(actor_user_id)
            recipients: list[tuple[str, str]] = []
            for user_id in self._role_user_ids("payroll_manager"):
                if user_id != actor_user_id:
                    recipients.append((user_id, "payroll_manager"))
            for user_id in self._role_user_ids("hr_admin"):
                if user_id != actor_user_id:
                    recipients.append((user_id, "hr_admin"))

            self._notify_many(
                recipients=recipients,
                type_=HrmsNotificationType.PAYROLL_MARKED_PAID,
                title=f"Payroll marked paid ({month})",
                message=(
                    f"Payroll run for {month} was marked paid for "
                    f"{len(seen_employee_user_ids)} employees."
                ),
                entity_type="hrms_payroll_run",
                entity_id=self._sid(payroll_run_id),
                data={
                    "route": "/hr/payroll/runs",
                    "payroll_run_id": self._sid(payroll_run_id),
                    "month": month,
                    "employee_count": len(seen_employee_user_ids),
                },
            )
        except Exception:
            return

    def notify_wrong_location_reviewed(
        self,
        *,
        attendance_id,
        employee_id,
        approved: bool,
    ) -> None:
        try:
            employee = self._employee_or_none(employee_id)
            employee_user_id = self._sid(employee.get("user_id")) if employee else None
            if not employee_user_id:
                return

            status_text = "approved" if approved else "rejected"
            type_ = (
                HrmsNotificationType.ATTENDANCE_WRONG_LOCATION_APPROVED
                if approved
                else HrmsNotificationType.ATTENDANCE_WRONG_LOCATION_REJECTED
            )

            self._notify_user(
                user_id=employee_user_id,
                role="employee",
                type_=type_,
                title=f"Wrong-location review {status_text}",
                message=f"Your wrong-location attendance review was {status_text}.",
                entity_type="hrms_attendance",
                entity_id=self._sid(attendance_id),
                data={
                    "route": "/hr/attendance",
                    "attendance_id": self._sid(attendance_id),
                    "status": status_text,
                },
            )
        except Exception:
            return

    def notify_early_leave_reviewed(
        self,
        *,
        attendance_id,
        employee_id,
        approved: bool,
    ) -> None:
        try:
            employee = self._employee_or_none(employee_id)
            employee_user_id = self._sid(employee.get("user_id")) if employee else None
            if not employee_user_id:
                return

            status_text = "approved" if approved else "rejected"
            type_ = (
                HrmsNotificationType.ATTENDANCE_EARLY_LEAVE_APPROVED
                if approved
                else HrmsNotificationType.ATTENDANCE_EARLY_LEAVE_REJECTED
            )

            self._notify_user(
                user_id=employee_user_id,
                role="employee",
                type_=type_,
                title=f"Early-leave review {status_text}",
                message=f"Your early-leave review was {status_text}.",
                entity_type="hrms_attendance",
                entity_id=self._sid(attendance_id),
                data={
                    "route": "/hr/attendance",
                    "attendance_id": self._sid(attendance_id),
                    "status": status_text,
                },
            )
        except Exception:
            return
