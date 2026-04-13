from __future__ import annotations


class ListEmployeesQuery:
    def __init__(self, *, employee_read_model) -> None:
        self.employee_read_model = employee_read_model

    def execute(
        self,
        *,
        q: str = "",
        page: int = 1,
        page_size: int = 10,
        show_deleted: str = "active",
    ):
        return self.employee_read_model.get_page(
            q=q,
            page=page,
            page_size=page_size,
            show_deleted=show_deleted,
        )