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
import type {
  AdminCreateStaff,
  AdminUpdateStaff,
} from "~/api/admin/staff/staff.dto";

const roleStaffOptionsRef = ref(roleStaffOptions);

export const staffFormSchema: Field<AdminCreateStaff>[] = [
  {
    row: [
      {
        key: "staff_id",
        label: "Staff ID",
        component: ElInput,
        componentProps: {
          placeholder: "Enter staff ID",
          suffixIcon: User,
        },
        formItemProps: {
          rules: [
            { required: true, message: "Staff ID required", trigger: "change" },
          ],
        },
      },
      {
        key: "staff_name",
        label: "Staff Name",
        component: ElInput,
        componentProps: {
          placeholder: "Enter staff name",
          suffixIcon: UserFilled,
        },
        formItemProps: {
          rules: [
            {
              validator: (rule, value, callback) => {
                const str = String(value ?? "").trim();
                if (!str) {
                  callback(new Error("Staff name is required"));
                } else if (/^\d+$/.test(str)) {
                  callback(new Error("Staff name cannot be a number"));
                } else {
                  callback();
                }
              },
              trigger: "change", // live validation while typing
            },
          ],
        },
      },
    ],
  },
  {
    row: [
      {
        key: "email",
        label: "Email",
        component: ElInput,
        componentProps: {
          placeholder: "Enter email",
          suffixIcon: Message,
        },
        formItemProps: {
          rules: [
            { required: true, message: "Email required", trigger: "change" },
            {
              type: "email",
              message: "Invalid email format",
              trigger: "change",
            },
          ],
        },
      },
      {
        key: "password",
        label: "Password",
        component: ElInput,
        componentProps: {
          placeholder: "Enter password",
          type: "password",
          suffixIcon: Lock,
        },
        formItemProps: {
          rules: [
            { required: true, message: "Password required", trigger: "change" },
            {
              min: 6,
              message: "Password must be at least 6 characters",
              trigger: "change",
            },
          ],
        },
      },
    ],
  },
  {
    row: [
      {
        key: "phone_number",
        label: "Phone",
        component: ElInput,
        componentProps: {
          placeholder: "Enter phone number",
          suffixIcon: Phone,
        },
        formItemProps: {
          rules: [
            {
              pattern: /^\d{8,15}$/,
              message: "Phone must be 8-15 digits",
              trigger: "change",
            },
          ],
        },
      },
      {
        key: "role",
        label: "Role",
        component: ElSelect,
        componentProps: {
          placeholder: "Select role",
          suffixIcon: Briefcase,
        },
        childComponent: ElOption,
        childComponentProps: {
          options: roleStaffOptionsRef,
        },
        formItemProps: {
          rules: [
            { required: true, message: "Role is required", trigger: "change" },
          ],
        },
      },
    ],
  },
  {
    row: [
      {
        key: "address",
        label: "Address",
        component: ElInput,
        componentProps: {
          placeholder: "Enter address",
          suffixIcon: Location,
        },
        formItemProps: {
          rules: [
            {
              required: true,
              message: "Address is required",
              trigger: "change",
            },
          ],
        },
      },
    ],
  },
];

export const staffFormSchemaEdit: Field<AdminUpdateStaff>[] = [
  {
    row: [
      {
        key: "staff_id",
        label: "Staff ID",
        component: ElInput,
        componentProps: {
          placeholder: "Enter staff ID",
          suffixIcon: User,
        },
        formItemProps: {
          rules: [
            { required: true, message: "Staff ID required", trigger: "change" },
          ],
        },
      },
      {
        key: "staff_name",
        label: "Staff Name",
        component: ElInput,
        componentProps: {
          placeholder: "Enter staff name",
          suffixIcon: UserFilled,
        },
        formItemProps: {
          rules: [
            {
              validator: (() => {
                let timeout: any;
                return (rule: any, value: any, callback: any) => {
                  clearTimeout(timeout);
                  timeout = setTimeout(() => {
                    const str = String(value ?? "").trim();
                    if (!str) {
                      callback(new Error("Staff name is required"));
                    } else if (/^\d+$/.test(str)) {
                      callback(new Error("Staff name cannot be a number"));
                    } else {
                      callback();
                    }
                  }, 300); // 300ms debounce
                };
              })(),
              trigger: "change",
            },
          ],
        },
      },
    ],
  },
  {
    row: [
      {
        key: "phone_number",
        label: "Phone",
        component: ElInput,
        componentProps: {
          placeholder: "Enter phone number",
          suffixIcon: Phone,
        },
        formItemProps: {
          rules: [
            {
              pattern: /^\d{8,15}$/,
              message: "Phone must be 8-15 digits",
              trigger: "change",
            },
          ],
        },
      },
      {
        key: "role",
        label: "Role",
        component: ElSelect,
        componentProps: {
          placeholder: "Select role",
          suffixIcon: Briefcase,
        },
        childComponent: ElOption,
        childComponentProps: {
          options: roleStaffOptionsRef,
        },
        formItemProps: {
          rules: [
            { required: true, message: "Role is required", trigger: "change" },
          ],
        },
      },
    ],
  },
  {
    row: [
      {
        key: "address",
        label: "Address",
        component: ElInput,
        componentProps: {
          placeholder: "Enter address",
          suffixIcon: Location,
        },
        formItemProps: {
          rules: [
            {
              required: true,
              message: "Address is required",
              trigger: "change",
            },
          ],
        },
      },
    ],
  },
];
