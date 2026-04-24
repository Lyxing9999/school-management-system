from __future__ import annotations


class GetEarlyLeaveReportQuery:
    def __init__(self, *, employee_read_model, attendance_read_model) -> None:
        self.employee_read_model = employee_read_model
        self.attendance_read_model = attendance_read_model

    def execute(
        self,
        *,
        manager_user_id=None,
        page: int = 1,
        page_size: int = 10,
        start_date=None,
        end_date=None,
        review_status: str | None = None,
    ):
        employee_ids = None
        if manager_user_id:
            employees = self.employee_read_model.list_team_by_manager_user_id(
                manager_user_id=manager_user_id,
                show_deleted="active",
            )
            employee_ids = [item.get("_id") for item in employees if item.get("_id")]
            if not employee_ids:
                return [], 0

        return self.attendance_read_model.list_early_leave_cases(
            employee_ids=employee_ids,
            start_date=start_date,
            end_date=end_date,
            review_status=review_status,
            page=page,
            limit=page_size,
        )
