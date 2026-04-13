from __future__ import annotations

from typing import Any


class ListEmployeesWithAccountsQuery:
    ALLOWED_SHOW_DELETED = {"active", "deleted", "all"}

    def __init__(self, *, employee_read_model, iam_gateway) -> None:
        self.employee_read_model = employee_read_model
        self.iam_gateway = iam_gateway

    def _normalize_q(self, value: str | None) -> str:
        return str(value or "").strip()

    def _normalize_page(self, value: int | str | None) -> int:
        try:
            return max(1, int(value or 1))
        except (TypeError, ValueError):
            return 1

    def _normalize_page_size(self, value: int | str | None) -> int:
        try:
            return min(max(1, int(value or 10)), 100)
        except (TypeError, ValueError):
            return 10

    def _normalize_show_deleted(self, value: str | None) -> str:
        normalized = str(value or "active").strip().lower()
        if normalized not in self.ALLOWED_SHOW_DELETED:
            raise ValueError(
                f"Invalid show_deleted='{normalized}'. "
                f"Allowed values: {sorted(self.ALLOWED_SHOW_DELETED)}"
            )
        return normalized

    def _build_item(
        self,
        *,
        employee: dict[str, Any],
        account: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "employee": employee,
            "account": account,
            "has_account": account is not None,
        }

    def execute(
        self,
        *,
        q: str = "",
        page: int = 1,
        page_size: int = 10,
        show_deleted: str = "active",
    ) -> tuple[list[dict[str, Any]], int]:
        q = self._normalize_q(q)
        page = self._normalize_page(page)
        page_size = self._normalize_page_size(page_size)
        show_deleted = self._normalize_show_deleted(show_deleted)

        employees, total = self.employee_read_model.get_page(
            q=q,
            page=page,
            page_size=page_size,
            show_deleted=show_deleted,
        )

        user_ids = [
            employee.get("user_id")
            for employee in employees
            if employee.get("user_id")
        ]

        account_map = self.iam_gateway.get_account_summaries_by_user_ids(user_ids)

        items: list[dict[str, Any]] = []
        for employee in employees:
            user_id = employee.get("user_id")
            account = account_map.get(str(user_id)) if user_id else None
            items.append(self._build_item(employee=employee, account=account))

        return items, int(total)