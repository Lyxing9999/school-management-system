import { roleUserOptions } from "~/utils/constants/roles";
import type { Field } from "~/components/types/form";
import { ElInput, ElSelect, ElOption } from "element-plus";
import { UserFilled, Lock } from "@element-plus/icons-vue";
import { UserRole } from "~/api/types/enums/role.enum";
import type { AdminCreateUser, AdminUpdateUser } from "~/api/admin/admin.dto";
export const userFormData: AdminCreateUser = {
  username: "",
  email: "",
  password: "",
  role: UserRole.STUDENT,
};
export const userFormDataEdit: AdminUpdateUser = userFormData;
const roleOptionsRef = ref(roleUserOptions);
export const userFormSchema: Field<AdminCreateUser>[] = [
  {
    key: "username",
    labelWidth: "100px",
    label: "Username",
    labelPosition: "left",
    component: ElInput,
    componentProps: {
      placeholder: "Enter username",
      suffixIcon: UserFilled,
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
      suffixIcon: UserFilled,
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
    key: "role",
    labelWidth: "100px",
    label: "Role",
    labelPosition: "left",
    component: ElSelect,
    componentProps: {
      placeholder: "Select role",
      style: "width: 150px",
    },
    childComponent: ElOption,
    childComponentProps: {
      options: roleOptionsRef,
    },
  },
];

export const userFormSchemaEdit: Field<AdminUpdateUser>[] = userFormSchema.map(
  (f) => {
    const field = { ...f };

    if (field.key === "password") {
      field.componentProps = {
        ...field.componentProps,
        placeholder: "Leave blank to keep current password",
      };
      field.rules = [];
    }

    if (field.key === "role") {
      field.componentProps = {
        ...field.componentProps,
        disabled: true,
      };
    }
    return field as Field<AdminUpdateUser>;
  }
);
