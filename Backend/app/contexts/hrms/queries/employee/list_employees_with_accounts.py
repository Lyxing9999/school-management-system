from __future__ import annotations


class ListEmployeesWithAccountsQuery:
    def __init__(self, *, employee_read_model, iam_gateway) -> None:
        self.employee_read_model = employee_read_model
        self.iam_gateway = iam_gateway

    def execute(
        self,
        *,
        q: str = "",
        page: int = 1,
        page_size: int = 10,
        show_deleted: str = "active",
    ):
        employees, total = self.employee_read_model.get_page(
            q=q,
            page=page,
            page_size=page_size,
            show_deleted=show_deleted,
        )

        user_ids = [item.get("user_id") for item in employees if item.get("user_id")]
        account_map = self.iam_gateway.get_account_summaries_by_user_ids(user_ids)

        items = []
        for employee in employees:
            user_id = employee.get("user_id")
            account = account_map.get(str(user_id)) if user_id else None

            items.append({
                "employee": employee,
                "account": account,
            })

        return items, total