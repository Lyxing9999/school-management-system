from __future__ import annotations


class ListOvertimeRequestsQuery:
    def __init__(self, *, employee_read_model, overtime_read_model) -> None:
        self.employee_read_model = employee_read_model
        self.overtime_read_model = overtime_read_model

    def execute(
        self,
        *,
        manager_user_id=None,
        employee_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        scoped_employee_ids = None
        if manager_user_id:
            employees = self.employee_read_model.list_team_by_manager_user_id(
                manager_user_id=manager_user_id,
                show_deleted="active",
            )
            team_ids = [item.get("_id") for item in employees if item.get("_id")]
            if not team_ids:
                return [], 0

            if employee_id:
                team_id_set = {str(item) for item in team_ids}
                if str(employee_id) not in team_id_set:
                    return [], 0
            else:
                scoped_employee_ids = team_ids

        return self.overtime_read_model.list_overtime_requests(
            employee_id=employee_id,
            employee_ids=scoped_employee_ids,
            status=status,
            page=page,
            limit=limit,
        )
