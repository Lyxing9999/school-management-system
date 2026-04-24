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

            normalized_review_status = str(
                row.get("location_review_status") or ""
            ).strip().lower()
            status_value = str(row.get("status") or "").strip().lower()
            if not normalized_review_status:
                legacy_map = {
                    "wrong_location_pending": "pending",
                    "wrong_location_approved": "approved",
                    "wrong_location_rejected": "rejected",
                }
                normalized_review_status = legacy_map.get(status_value, "")
                if normalized_review_status:
                    row["location_review_status"] = normalized_review_status or None

            row["wrong_location_status"] = (
                f"wrong_location_{normalized_review_status}"
                if normalized_review_status in {"pending", "approved", "rejected"}
                else None
            )

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

    def enrich_leave_balance_records(self, rows: list[dict]) -> list[dict]:
        employee_ids = self._collect(rows, "employee_id")
        user_ids = self._collect(rows, "manager_user_id")

        employee_map = self._resolver.resolve_employees_by_ids(employee_ids)
        user_map = self._resolver.resolve_users_by_ids(user_ids)

        for row in rows:
            employee_id = self._id(row.get("employee_id"))
            employee = employee_map.get(employee_id) if employee_id else None
            row["employee_name"] = (
                str(row.get("employee_name") or "").strip()
                or self._resolver.employee_name(employee)
            )

            manager_user_id = self._id(row.get("manager_user_id"))
            manager_user = user_map.get(manager_user_id) if manager_user_id else None
            row["manager_name"] = self._resolver.user_account_name(manager_user)

        return rows

    def enrich_overtime_records(self, rows: list[dict]) -> list[dict]:
        employee_ids = self._collect(rows, "employee_id", "manager_id")
        user_ids = self._collect(rows, "manager_user_id", "manager_id", "created_by")
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
                elif manager_id in user_map:
                    row["manager_user_id"] = manager_id
                    manager_user_id = manager_id

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

    @staticmethod
    def _entity_type_label(entity_type: str | None) -> str:
        text = str(entity_type or "").strip().lower()
        labels = {
            "attendance": "Attendance",
            "employee": "Employee",
            "leave": "Leave Request",
            "overtime": "Overtime Request",
            "payroll_run": "Payroll Run",
            "payslip": "Payslip",
            "work_location": "Work Location",
            "working_schedule": "Working Schedule",
            "public_holiday": "Public Holiday",
            "deduction_rule": "Deduction Rule",
        }
        if text in labels:
            return labels[text]
        if not text:
            return "Record"
        return text.replace("_", " ").title()

    def enrich_audit_records(self, rows: list[dict]) -> list[dict]:
        actor_ids = self._collect(rows, "actor_id")

        employee_ids: set[str] = set(actor_ids)
        schedule_ids: set[str] = set()
        location_ids: set[str] = set()
        payroll_run_ids: set[str] = set()
        detail_user_ids: set[str] = set()

        detail_user_fields = (
            "user_id",
            "manager_user_id",
            "created_by",
            "deleted_by",
            "generated_by",
            "early_leave_reviewed_by",
            "location_reviewed_by",
            "reviewed_by",
            "approved_by",
            "actor_user_id",
        )

        for row in rows:
            entity_type = str(row.get("entity_type") or "").strip().lower()
            entity_id = self._id(row.get("entity_id"))
            details = row.get("details")
            details = details if isinstance(details, dict) else {}

            details_employee_id = self._id(details.get("employee_id"))
            details_schedule_id = self._id(details.get("schedule_id"))
            details_primary_location_id = self._id(
                details.get("work_location_id") or details.get("location_id")
            )
            details_payroll_run_id = self._id(details.get("payroll_run_id"))
            details_manager_id = self._id(details.get("manager_id"))

            if details_employee_id:
                employee_ids.add(details_employee_id)
            if details_schedule_id:
                schedule_ids.add(details_schedule_id)
            if details_primary_location_id:
                location_ids.add(details_primary_location_id)
            if details_payroll_run_id:
                payroll_run_ids.add(details_payroll_run_id)
            if details_manager_id:
                # manager_id in legacy overtime audit can be either employee id or user id.
                employee_ids.add(details_manager_id)
                detail_user_ids.add(details_manager_id)

            for field in detail_user_fields:
                user_id = self._id(details.get(field))
                if user_id:
                    detail_user_ids.add(user_id)

            if entity_type == "employee" and entity_id:
                employee_ids.add(entity_id)
            if entity_type == "working_schedule" and entity_id:
                schedule_ids.add(entity_id)
            if entity_type == "work_location" and entity_id:
                location_ids.add(entity_id)
            if entity_type == "payroll_run" and entity_id:
                payroll_run_ids.add(entity_id)

        user_map = self._resolver.resolve_users_by_ids(actor_ids | detail_user_ids)
        employee_map = self._resolver.resolve_employees_by_ids(employee_ids)
        schedule_map = self._resolver.resolve_working_schedules_by_ids(schedule_ids)
        location_map = self._resolver.resolve_work_locations_by_ids(location_ids)
        payroll_map = self._resolver.resolve_payroll_runs_by_ids(payroll_run_ids)

        actor_bridged_user_ids: set[str] = set()
        for actor_id in actor_ids:
            actor_employee = employee_map.get(actor_id)
            bridged_user_id = (
                self._id(actor_employee.get("user_id")) if actor_employee else None
            )
            if bridged_user_id:
                actor_bridged_user_ids.add(bridged_user_id)
        if actor_bridged_user_ids:
            user_map.update(self._resolver.resolve_users_by_ids(actor_bridged_user_ids))

        for row in rows:
            row_details = row.get("details")
            row_details = row_details if isinstance(row_details, dict) else {}
            actor_id = self._id(row.get("actor_id")) or self._id(
                row_details.get("actor_user_id")
            )
            actor = user_map.get(actor_id) if actor_id else None
            actor_name = self._resolver.user_account_name(actor)
            actor_email = self._resolver.user_account_email(actor)

            if not actor_name and actor_id:
                actor_employee = employee_map.get(actor_id)
                bridged_user_id = (
                    self._id(actor_employee.get("user_id")) if actor_employee else None
                )
                bridged_user = user_map.get(bridged_user_id) if bridged_user_id else None
                actor_name = self._resolver.user_account_name(
                    bridged_user
                ) or self._resolver.employee_name(actor_employee)
                actor_email = actor_email or self._resolver.user_account_email(bridged_user)
                if bridged_user_id:
                    row["actor_user_id"] = bridged_user_id

            row["actor_name"] = actor_name
            row["actor_email"] = actor_email

            entity_type = str(row.get("entity_type") or "").strip().lower()
            entity_id = self._id(row.get("entity_id"))
            details = row.get("details")
            details = details if isinstance(details, dict) else {}
            details_view = dict(details)

            details_employee_id = self._id(details.get("employee_id"))
            details_schedule_id = self._id(details.get("schedule_id"))
            details_work_location_id = self._id(details.get("work_location_id"))
            details_location_id = self._id(details.get("location_id"))
            details_primary_location_id = self._id(
                details.get("work_location_id") or details.get("location_id")
            )
            details_payroll_run_id = self._id(details.get("payroll_run_id"))
            details_manager_id = self._id(details.get("manager_id"))

            employee_name = self._resolver.employee_name(
                employee_map.get(details_employee_id) if details_employee_id else None
            )
            if employee_name:
                details_view["employee_name"] = employee_name

            schedule_name = self._resolver.schedule_name(
                schedule_map.get(details_schedule_id) if details_schedule_id else None
            )
            if schedule_name:
                details_view["schedule_name"] = schedule_name

            location_name = self._resolver.location_name(
                location_map.get(details_primary_location_id)
                if details_primary_location_id
                else None
            )
            if location_name:
                if details_work_location_id:
                    details_view["work_location_name"] = location_name
                if details_location_id or details_primary_location_id:
                    details_view["location_name"] = location_name

            payroll_run = payroll_map.get(details_payroll_run_id) if details_payroll_run_id else None
            payroll_month = self._resolver.payroll_month(payroll_run)
            payroll_run_label = self._resolver.payroll_run_label(payroll_run)
            if payroll_month:
                details_view["payroll_month"] = payroll_month
            if payroll_run_label:
                details_view["payroll_run_label"] = payroll_run_label

            user_id = self._id(details.get("user_id"))
            user = user_map.get(user_id) if user_id else None
            account_name = self._resolver.user_account_name(user)
            account_email = self._resolver.user_account_email(user)
            if account_name:
                details_view["account_name"] = account_name
            if account_email:
                details_view["account_email"] = account_email

            manager_user_id = self._id(details.get("manager_user_id"))
            manager_user = user_map.get(manager_user_id) if manager_user_id else None
            manager_name = self._resolver.user_account_name(manager_user)
            if not manager_name and details_manager_id:
                manager_name = self._resolver.user_account_name(
                    user_map.get(details_manager_id)
                ) or self._resolver.employee_name(employee_map.get(details_manager_id))
            if manager_name:
                details_view["manager_name"] = manager_name

            created_by = self._id(details.get("created_by"))
            creator = user_map.get(created_by) if created_by else None
            created_by_name = self._resolver.user_account_name(creator)
            if created_by_name:
                details_view["created_by_name"] = created_by_name

            deleted_by = self._id(details.get("deleted_by"))
            deleter = user_map.get(deleted_by) if deleted_by else None
            deleted_by_name = self._resolver.user_account_name(deleter)
            if deleted_by_name:
                details_view["deleted_by_name"] = deleted_by_name

            generated_by = self._id(details.get("generated_by"))
            generator = user_map.get(generated_by) if generated_by else None
            generated_by_name = self._resolver.user_account_name(generator)
            if generated_by_name:
                details_view["generated_by_name"] = generated_by_name

            early_leave_reviewed_by = self._id(details.get("early_leave_reviewed_by"))
            early_reviewer = (
                user_map.get(early_leave_reviewed_by)
                if early_leave_reviewed_by
                else None
            )
            early_leave_reviewed_by_name = self._resolver.user_account_name(early_reviewer)
            if early_leave_reviewed_by_name:
                details_view["early_leave_reviewed_by_name"] = early_leave_reviewed_by_name

            location_reviewed_by = self._id(details.get("location_reviewed_by"))
            location_reviewer = (
                user_map.get(location_reviewed_by)
                if location_reviewed_by
                else None
            )
            location_reviewed_by_name = self._resolver.user_account_name(location_reviewer)
            if location_reviewed_by_name:
                details_view["location_reviewed_by_name"] = location_reviewed_by_name

            reviewed_by = self._id(details.get("reviewed_by")) or self._id(
                details.get("approved_by")
            )
            reviewer = user_map.get(reviewed_by) if reviewed_by else None
            reviewed_by_name = self._resolver.user_account_name(reviewer)
            if reviewed_by_name:
                details_view["reviewed_by_name"] = reviewed_by_name

            entity_name: str | None = None
            if entity_type == "employee":
                entity_name = self._resolver.employee_name(
                    employee_map.get(entity_id) if entity_id else None
                )
            elif entity_type == "working_schedule":
                entity_name = self._resolver.schedule_name(
                    schedule_map.get(entity_id) if entity_id else None
                )
            elif entity_type == "work_location":
                entity_name = self._resolver.location_name(
                    location_map.get(entity_id) if entity_id else None
                )
            elif entity_type == "payroll_run":
                payroll = payroll_map.get(entity_id) if entity_id else None
                entity_name = self._resolver.payroll_run_label(payroll)

            if not entity_name and employee_name and entity_type in {
                "attendance",
                "leave",
                "overtime",
                "payslip",
            }:
                entity_name = f"{self._entity_type_label(entity_type)} • {employee_name}"

            if not entity_name and details_schedule_id:
                entity_name = self._resolver.schedule_name(
                    schedule_map.get(details_schedule_id)
                )
            if not entity_name and details_primary_location_id:
                entity_name = self._resolver.location_name(
                    location_map.get(details_primary_location_id)
                )
            if not entity_name and details_payroll_run_id:
                entity_name = self._resolver.payroll_run_label(
                    payroll_map.get(details_payroll_run_id)
                )

            row["entity_name"] = entity_name or self._entity_type_label(entity_type)
            row["details"] = details_view

        return rows

    def enrich_single(self, row: dict | None, *, kind: str) -> dict | None:
        if not row:
            return row

        handlers = {
            "employee": self.enrich_employee_records,
            "employee_account": self.enrich_employee_account_records,
            "attendance": self.enrich_attendance_records,
            "leave": self.enrich_leave_records,
            "leave_balance": self.enrich_leave_balance_records,
            "overtime": self.enrich_overtime_records,
            "payroll_run": self.enrich_payroll_run_records,
            "payslip": self.enrich_payslip_records,
            "work_location": self.enrich_work_location_records,
            "working_schedule": self.enrich_working_schedule_records,
            "public_holiday": self.enrich_public_holiday_records,
            "deduction_rule": self.enrich_deduction_rule_records,
            "audit_log": self.enrich_audit_records,
        }
        handler = handlers.get(kind)
        if handler is None:
            return row

        handler([row])
        return row
