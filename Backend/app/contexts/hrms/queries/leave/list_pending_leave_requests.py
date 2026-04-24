from __future__ import annotations


class ListPendingLeaveRequestsQuery:
    def __init__(self, *, employee_read_model, leave_repository) -> None:
        self.employee_read_model = employee_read_model
        self.leave_repository = leave_repository

    def execute(self, *, manager_user_id=None, page: int = 1, page_size: int = 10):
        scoped_employee_ids = None
        if manager_user_id:
            employees = self.employee_read_model.list_team_by_manager_user_id(
                manager_user_id=manager_user_id,
                show_deleted="active",
            )
            scoped_employee_ids = [item.get("_id") for item in employees if item.get("_id")]
            if not scoped_employee_ids:
                return [], 0

        return self.leave_repository.list_requests(
            employee_ids=scoped_employee_ids,
            status="pending",
            page=page,
            page_size=page_size,
        )
