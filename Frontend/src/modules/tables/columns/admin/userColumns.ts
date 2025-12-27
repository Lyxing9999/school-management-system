import type { ColumnConfig } from "~/components/types/tableEdit";
import { ElInput, ElDatePicker, ElTag } from "element-plus";
import { h } from "vue";
import type { AdminGetUserItemData } from "~/api/admin/user/user.dto";

export const userColumns: ColumnConfig<AdminGetUserItemData>[] = [
  {
    field: "username",
    label: "Username",
    sortable: true,
    controls: false,
    autoSave: true,
    controlsSlot: true,
    minWidth: "150px",
    rules: [
      { required: true, message: "Please input username", trigger: "blur" },
      { min: 6, message: "At least 6 characters", trigger: "blur" },
      { max: 20, message: "Max 20 characters", trigger: "blur" },
      {
        pattern: /^[A-Za-z]+$/,
        message: "Only letters allowed (no numbers, no spaces)",
      },
    ],
    component: ElInput,
    componentProps: { placeholder: "Enter username" },
  },
  {
    field: "email",
    label: "Email",
    controls: false,
    autoSave: true,
    controlsSlot: true,
    minWidth: "300px",

    component: ElInput,
    componentProps: {
      placeholder: "Enter email",
      class: "w-full",
      style: { width: "100%" }, // important in tables
    },

    childComponentProps: { appendValue: "@gmail.com" },

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
    field: "status",
    label: "Status",
    width: "130px",
    useSlot: true,
    slotName: "status",
  },
  {
    field: "role",
    label: "Role",
    width: "120px",
    align: "center",
    render: (row: AdminGetUserItemData, field: keyof AdminGetUserItemData) => {
      const role = row[field];
      let type: "success" | "danger" | "warning" = "success";
      if (role === "admin") type = "danger";
      else if (role === "teacher") type = "warning";
      return h(ElTag, { type }, role);
    },
  },

  {
    field: "created_by_name",
    label: "Created By",
    inlineEditActive: true,
    controls: false,
    controlsSlot: false,
    minWidth: "140px",
    align: "center",
    render: (row: AdminGetUserItemData, field: keyof AdminGetUserItemData) =>
      h("span", { style: { color: "#999" } }, row[field]),
  },

  {
    field: "id",
    operation: true,
    label: "Operation",
    inlineEditActive: false,
    align: "center",
    minWidth: "200px",
    smartProps: {},
  },
];
