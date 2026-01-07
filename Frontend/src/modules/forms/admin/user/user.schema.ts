import { computed } from "vue";
import type { FormItemRule } from "element-plus";
import { ElInput, ElSelect, ElOption } from "element-plus";

import { roleUserOptions } from "~/utils/constants/roles";
import type { Field } from "~/components/types/form";
import type {
  AdminCreateUser,
  AdminUpdateUser,
} from "~/api/admin/user/user.dto";

/** ---- reusable rules (product-ready defaults) ---- */

const usernameRules: FormItemRule[] = [
  {
    required: true,
    message: "Username is required.",
    trigger: ["blur", "change"],
  },
  {
    min: 3,
    max: 30,
    message: "Username must be 3–30 characters.",
    trigger: ["blur", "change"],
  },
  {
    pattern: /^[a-zA-Z0-9._-]+$/,
    message: "Use letters, numbers, dot (.), underscore (_), or dash (-) only.",
    trigger: ["blur", "change"],
  },
];

const emailRules: FormItemRule[] = [
  {
    required: true,
    message: "Email is required.",
    trigger: ["blur", "change"],
  },
  {
    type: "email",
    message: "Please enter a valid email address.",
    trigger: ["blur", "change"],
  },
];

const passwordRulesCreate: FormItemRule[] = [
  {
    required: true,
    message: "Password is required.",
    trigger: ["blur", "change"],
  },
  {
    min: 8,
    message: "Password must be at least 8 characters.",
    trigger: ["blur", "change"],
  },
];

const passwordRulesEdit: FormItemRule[] = [
  {
    validator: (_rule, value: string, callback) => {
      // In edit: empty = keep old password
      if (!value) return callback();
      if (String(value).length < 8)
        return callback(new Error("Password must be at least 8 characters."));
      return callback();
    },
    trigger: ["blur", "change"],
  },
];

const roleRules: FormItemRule[] = [
  { required: true, message: "Role is required.", trigger: ["change"] },
];

/** options list (computed to keep it reactive-friendly) */
const roleOptions = computed(() => roleUserOptions);

/** ---------------- CREATE schema ---------------- */
export const userFormSchema: Field<AdminCreateUser>[] = [
  {
    key: "username",
    label: "Username",
    component: ElInput,
    formItemProps: {
      prop: "username",
      rules: usernameRules,
    },
    componentProps: {
      clearable: true,
      placeholder: "e.g. bunly_2003",
      autocomplete: "username",
      maxlength: 30,
      showWordLimit: true,
    },
  },
  {
    key: "email",
    label: "Email",
    component: ElInput,
    formItemProps: {
      prop: "email",
      rules: emailRules,
    },
    componentProps: {
      clearable: true,
      placeholder: "e.g. bunly@example.com",
      autocomplete: "email",
      maxlength: 254,
    },
  },
  {
    key: "password",
    label: "Password",
    component: ElInput,
    formItemProps: {
      prop: "password",
      rules: passwordRulesCreate,
    },
    componentProps: {
      type: "password",
      showPassword: true,
      placeholder: "At least 8 characters",
      autocomplete: "new-password",
    },
  },
  {
    key: "role",
    label: "Role",
    component: ElSelect,
    childComponent: ElOption,
    formItemProps: {
      prop: "role",
      rules: roleRules,
    },
    componentProps: {
      placeholder: "Select a role",
      clearable: true,
      filterable: true,
      class: "w-full",
    },
    childComponentProps: {
      options: () => roleOptions.value, // [{ value, label }, ...]
      valueKey: "value",
      labelKey: "label",
    },
  },
];

/** ---------------- EDIT schema ----------------
 * - password becomes optional (blank = keep)
 * - role is disabled (optional; remove if you want to allow role changes)
 */
export const userFormSchemaEdit: Field<AdminUpdateUser>[] = userFormSchema.map(
  (f) => {
    const field = { ...f } as any;

    if (field.key === "password") {
      field.formItemProps = {
        ...(field.formItemProps ?? {}),
        rules: passwordRulesEdit,
      };
      field.componentProps = {
        ...(field.componentProps ?? {}),
        placeholder: "Leave blank to keep current password",
        autocomplete: "new-password",
      };
    }

    if (field.key === "role") {
      field.componentProps = {
        ...(field.componentProps ?? {}),
        disabled: true,
      };
    }

    return field as Field<AdminUpdateUser>;
  }
);
