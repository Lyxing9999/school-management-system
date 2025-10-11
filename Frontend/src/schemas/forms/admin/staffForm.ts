import { ref } from "vue";
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
import type { AdminCreateStaff, AdminUpdateStaff } from "~/api/admin/admin.dto";

const roleStaffOptionsRef = ref(roleStaffOptions);

export const staffFormData: AdminCreateStaff = {
  email: "",
  password: "",
  role: StaffRole.TEACHER,
  staff_id: "",
  staff_name: "",
  phone_number: "",
  address: "",
};

export const staffFormDataEdit: AdminUpdateStaff = {
  role: StaffRole.TEACHER,
  staff_id: "",
  staff_name: "",
  phone_number: "",
  address: "",
};

// ✅ Create Schema (4 rows, consistent label widths, aligned layout)
export const staffFormSchema: Field<AdminCreateStaff>[] = [
  {
    row: [
      {
        key: "staff_id",
        labelWidth: "100px",
        label: "Staff ID",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter staff ID",
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
    ],
  },
  {
    row: [
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
        rules: [
          { required: true, message: "Password required", trigger: "blur" },
        ],
      },
    ],
  },
  {
    row: [
      {
        key: "phone_number",
        labelWidth: "100px",
        label: "Phone",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter phone number",
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
          options: roleStaffOptionsRef,
        },
      },
    ],
  },
  {
    row: [
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
    ],
  },
];

// ✅ Edit Schema (same row pattern, minus email & password)
export const staffFormSchemaEdit: Field<AdminUpdateStaff>[] = [
  {
    row: [
      {
        key: "staff_id",
        labelWidth: "100px",
        label: "Staff ID",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter staff ID",
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
    ],
  },
  {
    row: [
      {
        key: "phone_number",
        labelWidth: "100px",
        label: "Phone",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter phone number",
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
          options: roleStaffOptionsRef,
        },
      },
    ],
  },
  {
    row: [
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
    ],
  },
];
