from __future__ import annotations

from typing import Any, Iterable

from bson import ObjectId

from app.contexts.hrms.composition.repositories import HrmsRepositories
from app.contexts.iam.read_models.iam_read_model import IAMReadModel
from app.contexts.shared.model_converter import mongo_converter


class HrmsRelationResolver:
    """
    Read-side resolver for HRMS relation display labels.

    This class resolves relation ids in batch and returns lookup maps that can be
    consumed by presentation enrichers. It intentionally does not mutate payloads.
    """

    def __init__(self, *, repositories: HrmsRepositories) -> None:
        self._repositories = repositories
        self._iam_read_model = IAMReadModel(repositories.db)
        self._payroll_run_collection = repositories.db["hr_payroll_runs"]

    @staticmethod
    def _to_oid(value: Any) -> ObjectId | None:
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and value.strip().lower() in {"", "null", "none", "undefined"}:
            return None
        return mongo_converter.convert_to_object_id(value)

    def _to_oid_list(self, values: Iterable[Any]) -> list[ObjectId]:
        out: list[ObjectId] = []
        seen: set[ObjectId] = set()
        for raw in values:
            oid = self._to_oid(raw)
            if oid and oid not in seen:
                seen.add(oid)
                out.append(oid)
        return out

    @staticmethod
    def _to_key(value: Any) -> str:
        return str(value)

    def resolve_employees_by_ids(self, ids: Iterable[Any]) -> dict[str, dict]:
        oids = self._to_oid_list(ids)
        if not oids:
            return {}

        rows = self._repositories.employee_read_model.list_by_ids(
            oids,
            show_deleted="all",
        )
        return {self._to_key(row.get("_id")): row for row in rows if row.get("_id")}

    def resolve_users_by_ids(self, ids: Iterable[Any]) -> dict[str, dict]:
        oids = self._to_oid_list(ids)
        if not oids:
            return {}

        rows = self._iam_read_model.list_by_ids(oids)
        return {self._to_key(row.get("_id")): row for row in rows if row.get("_id")}

    def resolve_work_locations_by_ids(self, ids: Iterable[Any]) -> dict[str, dict]:
        oids = self._to_oid_list(ids)
        if not oids:
            return {}

        rows = self._repositories.work_location_read_model.list_by_ids(
            oids,
            show_deleted="all",
        )
        return {self._to_key(row.get("_id")): row for row in rows if row.get("_id")}

    def resolve_working_schedules_by_ids(self, ids: Iterable[Any]) -> dict[str, dict]:
        oids = self._to_oid_list(ids)
        if not oids:
            return {}

        rows = self._repositories.working_schedule_read_model.list_by_ids(
            oids,
            show_deleted="all",
        )
        return {self._to_key(row.get("_id")): row for row in rows if row.get("_id")}

    def resolve_payroll_runs_by_ids(self, ids: Iterable[Any]) -> dict[str, dict]:
        oids = self._to_oid_list(ids)
        if not oids:
            return {}

        rows = list(
            self._payroll_run_collection.find(
                {"_id": {"$in": oids}},
            )
        )
        return {self._to_key(row.get("_id")): row for row in rows if row.get("_id")}

    @staticmethod
    def user_account_name(user: dict | None) -> str | None:
        if not user:
            return None
        username = str(user.get("username") or "").strip()
        if username:
            return username
        email = str(user.get("email") or "").strip()
        return email or None

    @staticmethod
    def user_account_email(user: dict | None) -> str | None:
        if not user:
            return None
        email = str(user.get("email") or "").strip()
        return email or None

    @staticmethod
    def employee_name(employee: dict | None) -> str | None:
        if not employee:
            return None
        full_name = str(employee.get("full_name") or "").strip()
        if full_name:
            return full_name
        code = str(employee.get("employee_code") or "").strip()
        return code or None

    @staticmethod
    def schedule_name(schedule: dict | None) -> str | None:
        if not schedule:
            return None
        name = str(schedule.get("name") or "").strip()
        return name or None

    @staticmethod
    def location_name(location: dict | None) -> str | None:
        if not location:
            return None
        name = str(location.get("name") or "").strip()
        return name or None

    @staticmethod
    def payroll_month(payroll_run: dict | None) -> str | None:
        if not payroll_run:
            return None
        month = str(payroll_run.get("month") or "").strip()
        return month or None

    @staticmethod
    def payroll_run_label(payroll_run: dict | None) -> str | None:
        month = HrmsRelationResolver.payroll_month(payroll_run)
        if not month:
            return None
        return f"Payroll {month}"
