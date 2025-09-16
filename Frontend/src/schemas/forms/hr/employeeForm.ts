import type { Field } from "~/components/types/form";
import { ElInput, ElSelect, ElOption, ElTag } from "element-plus";
import { reactive } from "vue";

export const formData = reactive({
  staff_id: "",
  staff_name: "",
  phone_number: "",
  email: "",
  password: "",
  role: "",
  address: "",
});

import {
  User,
  UserFilled,
  Phone,
  Lock,
  Message,
  Location,
  Briefcase,
} from "@element-plus/icons-vue";

export const employeeFormSchema: Field[] = [
  {
    key: "staff_id",
    labelWidth: "100px",
    label: "Staff ID",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter staff id",
      suffixIcon: User,
    },
  },
  {
    key: "staff_name",
    labelWidth: "100px",
    label: "Staff Name",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter staff name",
      suffixIcon: UserFilled,
    },
  },
  {
    key: "phone_number",
    labelWidth: "100px",
    label: "Phone",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter phone",
      suffixIcon: Phone,
    },
  },
  {
    key: "email",
    labelWidth: "100px",
    label: "Email",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter email",
      suffixIcon: Message,
    },
  },
  {
    key: "password",
    labelWidth: "100px",
    label: "Password",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter password",
      type: "password",
      suffixIcon: Lock,
    },
  },
  {
    key: "role",
    labelWidth: "100px",
    label: "Role",
    labelPosition: "left",
    component: ElSelect,
    componentProps: {
      placeholder: "Select role",
      suffixIcon: Briefcase,
    },
    childComponent: ElOption,
    childComponentProps: {
      options: [
        { value: "teacher", label: "Teacher" },
        { value: "academic", label: "Academic" },
        { value: "front_office", label: "Front Office" },
        { value: "finance", label: "Finance" },
        { value: "admin", label: "Admin" },
        { value: "hr", label: "HR" },
      ],
    },
  },
  {
    key: "address",
    labelWidth: "100px",
    label: "Address",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter address",
      suffixIcon: Location,
    },
  },
];

export const formDataEditEmployee = reactive({
  staff_id: "",
  staff_name: "",
  phone_number: "",
  permission: [],
  address: "",
});

export const employeeFormSchemaEdit: Field[] = [
  {
    key: "staff_id",
    labelWidth: "100px",
    label: "Staff ID",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter staff id",
      suffixIcon: User,
    },
  },
  {
    key: "staff_name",
    labelWidth: "100px",
    label: "Staff Name",
    labelPosition: "left",
    component: ElInput,
    componentProps: { placeholder: "Enter staff name", suffixIcon: UserFilled },
  },

  {
    key: "phone_number",
    labelWidth: "100px",
    label: "Phone",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter phone",
      suffixIcon: Phone,
    },
  },
  {
    key: "permissions",
    label: "Permissions",
    labelWidth: "100px",
    labelPosition: "left",
    displayOnly: true,
  },
];
