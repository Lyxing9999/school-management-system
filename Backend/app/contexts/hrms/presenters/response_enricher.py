from __future__ import annotations

from typing import Any, Iterable

from app.contexts.hrms.presenters.relation_resolver import HrmsRelationResolver


class HrmsResponseEnricher:
    """
    Central read-side payload enrichment for HRMS responses.

    Rules:
    - Keep ids intact for API actions/forms.
    - Add human-readable display fields in a consistent naming convention.
    - Resolve relations in batches to avoid N+1 route-level lookups.
    """

    def __init__(self, *, resolver: HrmsRelationResolver) -> None:
        self._resolver = resolver

    @staticmethod
    def _id(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    @staticmethod
    def _lifecycle(row: dict) -> dict:
        lifecycle = row.get("lifecycle")
        return lifecycle if isinstance(lifecycle, dict) else {}

    def _deleted_by(self, row: dict) -> str | None:
        direct = self._id(row.get("deleted_by"))
        if direct:
            return direct
        return self._id(self._lifecycle(row).get("deleted_by"))

    def _set_deleted_fields(self, row: dict, user_map: dict[str, dict]) -> None:
        deleted_by = self._deleted_by(row)
        if deleted_by:
            row["deleted_by"] = deleted_by
        user = user_map.get(deleted_by) if deleted_by else None
        row["deleted_by_name"] = self._resolver.user_account_name(user)

    @staticmethod
    def _collect(rows: Iterable[dict], *fields: str) -> set[str]:
        out: set[str] = set()
        for row in rows:
            for field in fields:
                value = row.get(field)
                if value is None:
                    continue
                text = str(value).strip()
                if text:
                    out.add(text)
        return out

    def enrich_employee_records(self, rows: list[dict]) -> list[dict]:
        user_ids = self._collect(rows, "user_id", "manager_user_id", "created_by")
        schedule_ids = self._collect(rows, "schedule_id")
        location_ids = self._collect(rows, "work_location_id")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids

        user_map = self._resolver.resolve_users_by_ids(user_ids)
        schedule_map = self._resolver.resolve_working_schedules_by_ids(schedule_ids)
        location_map = self._resolver.resolve_work_locations_by_ids(location_ids)

        for row in rows:
            row["employee_name"] = (
                str(row.get("employee_name") or "").strip()
                or str(row.get("full_name") or "").strip()
                or None
            )

            user_id = self._id(row.get("user_id"))
            user = user_map.get(user_id) if user_id else None
            row["account_name"] = self._resolver.user_account_name(user)
            row["account_email"] = self._resolver.user_account_email(user)

            manager_user_id = self._id(row.get("manager_user_id"))
            manager_user = user_map.get(manager_user_id) if manager_user_id else None
            row["manager_name"] = self._resolver.user_account_name(manager_user)

            created_by = self._id(row.get("created_by"))
            created_by_user = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(created_by_user)

            schedule_id = self._id(row.get("schedule_id"))
            schedule = schedule_map.get(schedule_id) if schedule_id else None
            row["schedule_name"] = self._resolver.schedule_name(schedule)

            work_location_id = self._id(row.get("work_location_id"))
            location = location_map.get(work_location_id) if work_location_id else None
            row["work_location_name"] = self._resolver.location_name(location)

            self._set_deleted_fields(row, user_map)

        return rows

    def enrich_employee_account_records(self, rows: list[dict]) -> list[dict]:
        account_ids = self._collect(rows, "id", "user_id")
        user_map = self._resolver.resolve_users_by_ids(account_ids)

        for row in rows:
            user_id = self._id(row.get("user_id")) or self._id(row.get("id"))
            if user_id:
                row["user_id"] = user_id

            user = user_map.get(user_id) if user_id else None
            row["account_name"] = (
                str(row.get("account_name") or "").strip()
                or self._resolver.user_account_name(user)
                or str(row.get("username") or "").strip()
                or str(row.get("email") or "").strip()
                or None
            )
            row["account_email"] = (
                str(row.get("account_email") or "").strip()
                or self._resolver.user_account_email(user)
                or str(row.get("email") or "").strip()
                or None
            )

        return rows

    def enrich_attendance_records(self, rows: list[dict]) -> list[dict]:
        employee_ids = self._collect(rows, "employee_id")
        schedule_ids = self._collect(rows, "schedule_id")
        location_ids = self._collect(rows, "location_id")
        user_ids = self._collect(
            rows,
            "location_reviewed_by",
            "early_leave_reviewed_by",
            "created_by",
        )
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids

        employee_map = self._resolver.resolve_employees_by_ids(employee_ids)
        schedule_map = self._resolver.resolve_working_schedules_by_ids(schedule_ids)
        location_map = self._resolver.resolve_work_locations_by_ids(location_ids)
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            employee_id = self._id(row.get("employee_id"))
            employee = employee_map.get(employee_id) if employee_id else None
            row["employee_name"] = self._resolver.employee_name(employee)

            schedule_id = self._id(row.get("schedule_id"))
            schedule = schedule_map.get(schedule_id) if schedule_id else None
            row["schedule_name"] = self._resolver.schedule_name(schedule)

            location_id = self._id(row.get("location_id"))
            location = location_map.get(location_id) if location_id else None
            row["location_name"] = self._resolver.location_name(location)

            location_reviewed_by = self._id(row.get("location_reviewed_by"))
            location_reviewer = user_map.get(location_reviewed_by) if location_reviewed_by else None
            row["location_reviewed_by_name"] = self._resolver.user_account_name(location_reviewer)

            early_leave_reviewed_by = self._id(row.get("early_leave_reviewed_by"))
            early_reviewer = user_map.get(early_leave_reviewed_by) if early_leave_reviewed_by else None
            row["early_leave_reviewed_by_name"] = self._resolver.user_account_name(early_reviewer)

            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)

            self._set_deleted_fields(row, user_map)

        return rows

    def enrich_leave_records(self, rows: list[dict]) -> list[dict]:
        employee_ids = self._collect(rows, "employee_id")
        user_ids = self._collect(rows, "manager_user_id", "created_by")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids

        employee_map = self._resolver.resolve_employees_by_ids(employee_ids)
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            employee_id = self._id(row.get("employee_id"))
            employee = employee_map.get(employee_id) if employee_id else None
            row["employee_name"] = self._resolver.employee_name(employee)

            manager_user_id = self._id(row.get("manager_user_id"))
            manager_user = user_map.get(manager_user_id) if manager_user_id else None
            row["manager_name"] = self._resolver.user_account_name(manager_user)

            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)

            self._set_deleted_fields(row, user_map)

        return rows

    def enrich_overtime_records(self, rows: list[dict]) -> list[dict]:
        employee_ids = self._collect(rows, "employee_id", "manager_id")
        user_ids = self._collect(rows, "manager_user_id", "created_by")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids

        employee_map = self._resolver.resolve_employees_by_ids(employee_ids)
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        # manager_id is legacy in overtime payloads. Bridge it to manager_user_id
        # when possible so downstream UI can use a stable manager_name field.
        for row in rows:
            manager_user_id = self._id(row.get("manager_user_id"))
            manager_id = self._id(row.get("manager_id"))
            if not manager_user_id and manager_id:
                manager_employee = employee_map.get(manager_id)
                bridged_user_id = self._id(manager_employee.get("user_id")) if manager_employee else None
                if bridged_user_id:
                    row["manager_user_id"] = bridged_user_id
                    manager_user_id = bridged_user_id
                    if bridged_user_id not in user_map:
                        user_map.update(self._resolver.resolve_users_by_ids([bridged_user_id]))

            employee_id = self._id(row.get("employee_id"))
            employee = employee_map.get(employee_id) if employee_id else None
            row["employee_name"] = self._resolver.employee_name(employee)

            manager_user = user_map.get(manager_user_id) if manager_user_id else None
            manager_name = self._resolver.user_account_name(manager_user)
            if not manager_name and manager_id:
                manager_name = self._resolver.employee_name(employee_map.get(manager_id))
            row["manager_name"] = manager_name

            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)

            self._set_deleted_fields(row, user_map)

        return rows

    def enrich_payroll_run_records(self, rows: list[dict]) -> list[dict]:
        user_ids = self._collect(rows, "generated_by", "created_by")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            generated_by = self._id(row.get("generated_by"))
            generated_user = user_map.get(generated_by) if generated_by else None
            row["generated_by_name"] = self._resolver.user_account_name(generated_user)

            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)

            month = str(row.get("payroll_month") or row.get("month") or "").strip()
            row["payroll_month"] = month or None
            row["payroll_run_label"] = f"Payroll {month}" if month else None

            self._set_deleted_fields(row, user_map)

        return rows

    def enrich_payslip_records(self, rows: list[dict]) -> list[dict]:
        employee_ids = self._collect(rows, "employee_id")
        payroll_run_ids = self._collect(rows, "payroll_run_id")
        user_ids = self._collect(rows, "created_by")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids

        employee_map = self._resolver.resolve_employees_by_ids(employee_ids)
        payroll_map = self._resolver.resolve_payroll_runs_by_ids(payroll_run_ids)
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            employee_id = self._id(row.get("employee_id"))
            employee = employee_map.get(employee_id) if employee_id else None
            row["employee_name"] = self._resolver.employee_name(employee)

            payroll_run_id = self._id(row.get("payroll_run_id"))
            payroll_run = payroll_map.get(payroll_run_id) if payroll_run_id else None

            month = (
                self._resolver.payroll_month(payroll_run)
                or str(row.get("month") or "").strip()
                or None
            )
            row["payroll_month"] = month
            row["payroll_run_label"] = (
                self._resolver.payroll_run_label(payroll_run)
                or (f"Payroll {month}" if month else None)
            )

            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)

            self._set_deleted_fields(row, user_map)

        return rows

    def enrich_work_location_records(self, rows: list[dict]) -> list[dict]:
        user_ids = self._collect(rows, "created_by")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            row["location_name"] = (
                str(row.get("location_name") or "").strip()
                or str(row.get("name") or "").strip()
                or None
            )
            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)
            self._set_deleted_fields(row, user_map)
        return rows

    def enrich_working_schedule_records(self, rows: list[dict]) -> list[dict]:
        user_ids = self._collect(rows, "created_by")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            row["schedule_name"] = (
                str(row.get("schedule_name") or "").strip()
                or str(row.get("name") or "").strip()
                or None
            )
            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)
            self._set_deleted_fields(row, user_map)
        return rows

    def enrich_public_holiday_records(self, rows: list[dict]) -> list[dict]:
        user_ids = self._collect(rows, "created_by")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)
            self._set_deleted_fields(row, user_map)
        return rows

    def enrich_deduction_rule_records(self, rows: list[dict]) -> list[dict]:
        user_ids = self._collect(rows, "created_by")
        deleted_ids = {self._deleted_by(row) for row in rows}
        deleted_ids = {x for x in deleted_ids if x}
        user_ids |= deleted_ids
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            created_by = self._id(row.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            row["created_by_name"] = self._resolver.user_account_name(creator)
            self._set_deleted_fields(row, user_map)
        return rows

    def enrich_single(self, row: dict | None, *, kind: str) -> dict | None:
        if not row:
            return row

        handlers = {
            "employee": self.enrich_employee_records,
            "employee_account": self.enrich_employee_account_records,
            "attendance": self.enrich_attendance_records,
            "leave": self.enrich_leave_records,
            "overtime": self.enrich_overtime_records,
            "payroll_run": self.enrich_payroll_run_records,
            "payslip": self.enrich_payslip_records,
            "work_location": self.enrich_work_location_records,
            "working_schedule": self.enrich_working_schedule_records,
            "public_holiday": self.enrich_public_holiday_records,
            "deduction_rule": self.enrich_deduction_rule_records,
        }
        handler = handlers.get(kind)
        if handler is None:
            return row

        handler([row])
        return row
