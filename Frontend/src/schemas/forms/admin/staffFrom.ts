import { reactive } from "vue";

import type { Field } from "~/components/types/form";
import { roleStaffOptions } from "~/utils/constants/roles";
import { ElInput, ElSelect, ElOption } from "element-plus";
import {
  Phone,
  Location,
  User,
  UserFilled,
  Lock,
  Message,
  Briefcase,
} from "@element-plus/icons-vue";
import { StaffRole } from "~/api/types/enums/role.enum";
import type { AdminCreateStaff } from "~/api/admin/admin.dto";
export const staffFormSchema: Field[] = [
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
    key: "email",
    labelWidth: "100px",
    label: "Email",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter email",
      suffixIcon: Message,
    },
    rules: [
      { required: true, message: "Email required", trigger: "blur" },
      {
        type: "email",
        message: "Enter a valid email",
        trigger: "blur",
      },
    ],
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
    rules: [{ required: true, message: "Password required", trigger: "blur" }],
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
      options: roleStaffOptions,
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

export const staffFormData = reactive<AdminCreateStaff>({
  username: "",
  email: "",
  password: "",
  role: StaffRole.TEACHER,
  staff_id: "",
  staff_name: "",
  phone_number: "",
  address: "",
});
