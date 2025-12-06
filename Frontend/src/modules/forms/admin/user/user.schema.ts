import { roleUserOptions } from "~/utils/constants/roles";
import type { Field } from "~/components/types/form";
import { ElInput, ElSelect, ElOption } from "element-plus";
import { UserFilled, Lock } from "@element-plus/icons-vue";
import type {
  AdminCreateUser,
  AdminUpdateUser,
} from "~/api/admin/user/user.dto";
const roleOptionsRef = ref(roleUserOptions);

export const userFormSchema: Field<AdminCreateUser>[] = [
  {
    key: "username",
    label: "Username",
    component: ElInput,
    formItemProps: {
      prop: "username",
      label: "Username",
      rules: [
        {
          required: true,
          message: "Username required",
          trigger: ["blur", "change"],
        },
      ],
    },
    componentProps: {
      clearable: true,
      placeholder: "Enter username",
    },
  },
  {
    key: "email",
    label: "Email",
    component: ElInput,
    formItemProps: {
      prop: "email",
      label: "Email",
      rules: [
        {
          required: true,
          message: "Email required",
          trigger: ["blur", "change"],
        },
        {
          type: "email",
          message: "Invalid email format",
          trigger: ["blur", "change"],
        },
      ],
    },
    componentProps: {
      clearable: true,
      placeholder: "Enter email",
    },
  },
  {
    key: "password",
    label: "Password",
    component: ElInput,
    formItemProps: {
      prop: "password",
      label: "Password",
      rules: [
        {
          required: true,
          message: "Password required",
          trigger: ["blur", "change"],
        },
      ],
    },
    componentProps: {
      type: "password",
      showPassword: true,
      placeholder: "Enter password",
    },
  },
  {
    key: "role",
    label: "Role",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      prop: "role",
      label: "Role",
      rules: [
        {
          required: true,
          message: "Role required",
          trigger: ["change"],
        },
      ],
    },
    componentProps: {
      placeholder: "Select role",
      clearable: true,
    },
    childComponentProps: {
      options: () => roleOptionsRef.value, // [{value, label}...]
      valueKey: "value",
      labelKey: "label",
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
      field.formItemProps = {
        ...field.formItemProps,
        rules: [],
      };
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
