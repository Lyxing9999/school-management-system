from __future__ import annotations

import math


class ListLeaveBalancesQuery:
    ANNUAL_ENTITLEMENT = 18

    def __init__(self, *, employee_read_model, leave_repository) -> None:
        self.employee_read_model = employee_read_model
        self.leave_repository = leave_repository

    def execute(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        employee_id: str | None = None,
        manager_user_id=None,
    ):
        page = max(1, int(page))
        page_size = max(1, int(page_size))
        keyword = str(q or "").strip().lower()

        employees: list[dict] = []
        total = 0

        if employee_id:
            row = self.employee_read_model.get_by_id(employee_id, show_deleted="active")
            if row and manager_user_id:
                employee_manager_user_id = row.get("manager_user_id")
                if not employee_manager_user_id or str(employee_manager_user_id) != str(manager_user_id):
                    row = None
            employees = [row] if row else []
            total = len(employees)
        elif manager_user_id:
            team_rows = self.employee_read_model.list_team_by_manager_user_id(
                manager_user_id=manager_user_id,
                show_deleted="active",
            )
            if keyword:
                team_rows = [
                    item
                    for item in team_rows
                    if keyword in " ".join(
                        [
                            str(item.get("employee_code") or ""),
                            str(item.get("full_name") or ""),
                            str(item.get("department") or ""),
                            str(item.get("position") or ""),
                        ]
                    ).lower()
                ]
            total = len(team_rows)
            start = (page - 1) * page_size
            employees = team_rows[start : start + page_size]
        else:
            employees, total = self.employee_read_model.get_page(
                page=page,
                page_size=page_size,
                q=q or "",
                show_deleted="active",
            )

        rows = [self._to_balance_row(employee) for employee in employees if employee]
        total_pages = max(1, math.ceil(total / page_size)) if total else 1

        return rows, int(total), page, page_size, total_pages

    def _to_balance_row(self, employee: dict) -> dict:
        employee_id = employee.get("_id")
        leave_items, _ = self.leave_repository.list_requests(
            employee_id=employee_id,
            page=1,
            page_size=2000,
        )

        approved_days = 0
        used_paid_days = 0
        pending_days = 0

        approved_annual_days = 0
        approved_sick_days = 0
        approved_unpaid_days = 0
        approved_other_days = 0

        last_approved_end_date = None

        for item in leave_items:
            status = item.status.value if hasattr(item.status, "value") else str(item.status)
            leave_type = (
                item.leave_type.value
                if hasattr(item.leave_type, "value")
                else str(item.leave_type)
            )
            days = int(item.total_days())

            if status == "pending":
                pending_days += days
                continue

            if status != "approved":
                continue

            approved_days += days
            if bool(item.is_paid):
                used_paid_days += days

            if leave_type == "annual":
                approved_annual_days += days
            elif leave_type == "sick":
                approved_sick_days += days
            elif leave_type == "unpaid":
                approved_unpaid_days += days
            else:
                approved_other_days += days

            if (
                last_approved_end_date is None
                or item.end_date > last_approved_end_date
            ):
                last_approved_end_date = item.end_date

        annual_entitlement = self.ANNUAL_ENTITLEMENT
        remaining_days = max(annual_entitlement - used_paid_days, 0)

        return {
            "employee_id": str(employee_id),
            "employee_name": str(employee.get("full_name") or "").strip() or None,
            "employee_code": str(employee.get("employee_code") or "").strip() or None,
            "department": str(employee.get("department") or "").strip() or None,
            "position": str(employee.get("position") or "").strip() or None,
            "employee_status": str(employee.get("status") or "").strip() or None,
            "manager_user_id": str(employee.get("manager_user_id") or "").strip() or None,
            "annual_entitlement": int(annual_entitlement),
            "used_days": int(used_paid_days),
            "remaining_days": int(remaining_days),
            "pending_days": int(pending_days),
            "approved_days": int(approved_days),
            "approved_annual_days": int(approved_annual_days),
            "approved_sick_days": int(approved_sick_days),
            "approved_unpaid_days": int(approved_unpaid_days),
            "approved_other_days": int(approved_other_days),
            "last_approved_end_date": (
                last_approved_end_date.isoformat() if last_approved_end_date else None
            ),
        }
