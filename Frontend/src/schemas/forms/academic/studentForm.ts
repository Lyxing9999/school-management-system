import { roleUserOptions } from "~/utils/constants/roles";
import type { Field } from "~/components/types/form";
import { ElInput, ElSelect, ElOption } from "element-plus";
import { UserFilled, Lock } from "@element-plus/icons-vue";
import type {
  AcademicCreateStudentData,
  AcademicUpdateStudentData,
} from "~/api/academic/academic.dto";
export const studentFormSchema: Field<AcademicCreateStudentData>[] = [
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
    component: ElInput, // readonly input instead of select
    componentProps: {
      placeholder: "Student",
      readonly: true,
      disabled: true,
      modelValue: "Student", // always show Student
    },
  },
];

export const studentFormData: AcademicCreateStudentData = {
  username: "",
  email: "",
  password: "",
};
export const studentFormDataEdit: AcademicUpdateStudentData = studentFormData;
export const studentFormSchemaEdit: Field<AcademicUpdateStudentData>[] =
  studentFormSchema.map((f) => {
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
    return field as Field<AcademicUpdateStudentData>;
  });

export {
  studentInfoFormDataEdit,
  studentInfoFormSchemaEdit,
} from "~/schemas/forms/admin/studentForm";
