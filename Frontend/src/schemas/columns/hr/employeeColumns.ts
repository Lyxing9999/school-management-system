import type { ColumnConfig } from "~/components/types/tableEdit";
import { userColumns } from "~/schemas/columns/admin/userColumns";

export const employeeColumns: ColumnConfig<any>[] = userColumns.map((col) => {
  if (col.field === "operation") {
    return {
      ...col,
      label: "Employee Actions",
      operation: true,
      width: "220px",
    };
  }
  return { ...col };
});
