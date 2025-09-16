import type { ColumnConfig } from "~/components/types/tableEdit";
import { ElInput, ElDatePicker, ElTag } from "element-plus";
import { h } from "vue";

export const userColumns: ColumnConfig<any>[] = [
  {
    field: "username",
    label: "Username",
    sortable: true,
    width: "180px",
    controls: false,
    autoSave: true,
    controlsSlot: true,
    rules: [
      { required: true, message: "Please input username", trigger: "blur" },
      { min: 6, message: "At least 3 characters", trigger: "blur" },
      { max: 20, message: "Max 20 characters", trigger: "blur" },
      {
        pattern: /^[A-Za-z]+$/,
        message: "Only letters allowed (no numbers, no spaces)",
      },
    ],
    component: ElInput,
    componentProps: {
      placeholder: "Enter username",
    },
  },

  {
    field: "email",
    label: "Email",
    controls: false,
    autoSave: true,
    controlsSlot: true,
    width: "220px",
    childComponentProps: {
      slots: {
        append: () => h("span", "@gmail.com"),
      },
      appendValue: "@gmail.com",
    },
    component: ElInput,
    componentProps: {
      placeholder: "Enter email",
    },
    rules: [
      { required: true, message: "Email required", trigger: "blur" },
      {
        pattern: /^[^@.]+$/,
        message: "Do not type @ or . — it will be added automatically",
        trigger: "blur",
      },
    ],
  },
  {
    field: "role",
    label: "Role",
    width: "150px",
    align: "center",
    render: (row: any, field: any) => {
      const role = row[field];
      let type: "success" | "danger" | "warning" = "success";

      if (role === "admin") type = "danger";
      else if (role === "teacher") type = "warning";
      else type = "success";
      return h(ElTag, { type }, role);
    },
  },
  {
    field: "created_by",
    label: "Created By",
    inlineEditActive: true,
    controls: false,
    controlsSlot: false,
    width: "180px",
    align: "center",
    render: (row: any, field: any) =>
      h("span", { style: { color: "#999" } }, row[field]),
  },
  {
    field: "created_at",
    label: "Created At",
    inlineEditActive: true,
    width: "200px",
    component: ElDatePicker,
    componentProps: {
      style: "width: 100%",
      readonly: true,
      disabled: true,
      format: "DD-MM-YYYY HH:mm:ss",
      type: "datetime",
      valueFormat: "YYYY-MM-DD HH:mm:ss",
    },
  },
  {
    field: "updated_at",
    label: "Updated At",
    width: "200px",
    inlineEditActive: true,
    component: ElDatePicker,
    componentProps: {
      style: "width: 100%",
      readonly: true,
      disabled: true,
      format: "DD-MM-YYYY HH:mm:ss",
      type: "datetime",
      valueFormat: "YYYY-MM-DD HH:mm:ss",
    },
  },
  {
    field: "operation",
    label: "Operation",
    fixed: "right",
    align: "center",
    width: "220px",
    operation: true,
    smartProps: {
      headerStyle: { background: "#6B3FA0", color: "#fff" },
      columnClass: "operation-column",
    },
  },
];
