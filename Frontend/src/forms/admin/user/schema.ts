import { roleUserOptions } from "~/utils/constants/roles";
import type { Field } from "~/components/types/form";
import { ElInput, ElSelect, ElOption } from "element-plus";
import { UserFilled, Lock } from "@element-plus/icons-vue";
import type { AdminCreateUser, AdminUpdateUser } from "~/api/admin/user/dto";
const roleOptionsRef = ref(roleUserOptions);

export const userFormSchema: Field<AdminCreateUser>[] = [
  {
    key: "username",
    formItemProps: { labelWidth: "100px", labelPosition: "left" },
    label: "Username",

    component: ElInput,
    componentProps: {
      placeholder: "Enter username",
      suffixIcon: UserFilled,
    },
  },
  {
    key: "email",
    formItemProps: {
      labelWidth: "100px",
      labelPosition: "left",
      rules: [
        {
          validator: (rule, value, callback) => {
            if (!value) return callback(new Error("Email required"));
            if (!value.includes("@"))
              return callback(new Error("Must contain @"));
            if (!value.endsWith(".com"))
              return callback(new Error("Must end with .com"));
            callback(); // valid
          },
          trigger: "change", // live validation
        },
      ],
    },
    label: "Email",
    component: ElInput,
    componentProps: {
      placeholder: "Enter email",
    },
  },
  {
    key: "password",
    formItemProps: {
      labelWidth: "100px",
      labelPosition: "left",
      rules: [
        {
          validator: (rule, value, callback) => {
            if (!value) return callback(new Error("Password required"));
            if (value.length < 6)
              return callback(
                new Error("Password must be at least 6 characters")
              );
            callback(); // valid
          },
          trigger: "change", // live validation
        },
      ],
    },
    label: "Password",
    component: ElInput,
    componentProps: {
      placeholder: "Enter password",
      type: "password",
      suffixIcon: Lock,
    },
  },
  {
    key: "role",
    formItemProps: { labelWidth: "100px", labelPosition: "left" },
    label: "Role",
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
