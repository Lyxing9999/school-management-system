import type { ColumnConfig } from "~/components/types/tableEdit";
import { ElInput, ElOption, ElSelect } from "element-plus";

export const classColumns: ColumnConfig<any>[] = [
  {
    field: "name",
    label: "Name",
    width: "150px",
    component: ElInput,
    componentProps: {
      placeholder: "Enter name",
    },
  },
  {
    field: "owner",
    label: "Owner",
    width: "150px",
    component: ElSelect,
    componentProps: {
      placeholder: "Enter owner",
    },
    childComponent: ElOption,
    childComponentProps: {
      options: [],
      valueKey: "value",
      labelKey: "label",
    },
  },
  {
    field: "grade",
    label: "Grade",
    width: "150px",
    component: ElInput,
    componentProps: {
      placeholder: "Enter grade",
    },
  },
  {
    field: "status",
    label: "Status",
    width: "150px",
    component: ElInput,
    componentProps: {
      placeholder: "Enter status",
    },
  },
  {
    field: "operation",
    label: "Operation",
    fixed: "right",
    align: "center",
    width: "120px",
    operation: true,
  },
];
