import type { Field } from "~/components/types/form";
import { ElInput } from "element-plus";
import { User, Message } from "@element-plus/icons-vue";
import type {
  AdminStudentInfoUpdate,
  GuardianInfo,
} from "~/api/admin/admin.dto";

const guardianFormData = <GuardianInfo>{
  name: "",
  phone: "",
  relation: "",
};

export const studentInfoFormData: AdminStudentInfoUpdate = {
  student_id: "",
  full_name: "",
  first_name: "",
  last_name: "",
  nickname: "",
  birth_date: "",
  gender: "",
  grade_level: 0,
  classes: [],
  enrollment_date: "",
  address: "",
  photo_url: "",
  guardian: guardianFormData,
  additional_info: {},
};

export const studentInfoFormSchema: Field<AdminStudentInfoUpdate>[] = [
  {
    row: [
      {
        key: "student_id",
        label: "Student ID",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElInput,
        componentProps: { placeholder: "Enter student id", suffixIcon: User },
      },
      {
        key: "full_name",
        label: "Full Name",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElInput,
        componentProps: { placeholder: "Enter full name", suffixIcon: Message },
        rules: [
          { required: true, message: "Full name required", trigger: "blur" },
        ],
      },
    ],
  },
  {
    row: [
      {
        key: "first_name",
        label: "First Name",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter first name",
          suffixIcon: Message,
        },
        rules: [
          { required: true, message: "First name required", trigger: "blur" },
        ],
      },
      {
        key: "last_name",
        label: "Last Name",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElInput,
        componentProps: { placeholder: "Enter last name", suffixIcon: Message },
        rules: [
          { required: true, message: "Last name required", trigger: "blur" },
        ],
      },
    ],
  },
  {
    row: [
      {
        key: "nickname",
        label: "Nickname",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElInput,
        componentProps: { placeholder: "Enter nickname", suffixIcon: Message },
        rules: [
          { required: true, message: "Nickname required", trigger: "blur" },
        ],
      },
      {
        key: "birth_date",
        label: "Birth Date",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter birth date",
          suffixIcon: Message,
        },
        rules: [
          { required: true, message: "Birth date required", trigger: "blur" },
        ],
      },
    ],
  },
  {
    row: [
      {
        key: "gender",
        label: "Gender",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElInput,
        componentProps: { placeholder: "Enter gender", suffixIcon: Message },
        rules: [
          { required: true, message: "Gender required", trigger: "blur" },
        ],
      },
      {
        key: "grade_level",
        label: "Grade Level",
        labelWidth: "120px",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter grade level",
          suffixIcon: Message,
        },
        rules: [
          { required: true, message: "Grade level required", trigger: "blur" },
        ],
      },
    ],
  },
  {
    row: [
      {
        key: "classes",
        label: "Classes",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElInput,
        componentProps: { placeholder: "Enter classes", suffixIcon: Message },
        rules: [
          { required: true, message: "Classes required", trigger: "blur" },
        ],
      },
      {
        key: "enrollment_date",
        label: "Enrollment Date",
        labelWidth: "140px",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter enrollment date",
          suffixIcon: Message,
        },
        rules: [
          {
            required: true,
            message: "Enrollment date required",
            trigger: "blur",
          },
        ],
      },
    ],
  },
  {
    row: [
      {
        key: "address",
        label: "Address",
        labelWidth: "120px",
        labelPosition: "left",
        component: ElInput,
        componentProps: { placeholder: "Enter address", suffixIcon: Message },
        rules: [
          { required: true, message: "Address required", trigger: "blur" },
        ],
      },
      {
        key: "photo_url",
        label: "Photo URL",
        labelWidth: "120px",
        labelPosition: "left",
        component: ElInput,
        componentProps: { placeholder: "Enter photo url", suffixIcon: Message },
        rules: [
          { required: true, message: "Photo url required", trigger: "blur" },
        ],
      },
    ],
  },
  {
    row: [
      {
        key: "additional_info",
        label: "Additional Info",
        labelWidth: "120px",
        labelPosition: "left",
        component: ElInput,
        componentProps: {
          placeholder: "Enter additional info",
          suffixIcon: Message,
        },
        rules: [
          {
            required: true,
            message: "Additional info required",
            trigger: "blur",
          },
        ],
      },
    ],
  },
];

export const studentInfoFormDataEdit = studentInfoFormData;
export const studentInfoFormSchemaEdit: Field<AdminStudentInfoUpdate>[] =
  studentInfoFormSchema;
