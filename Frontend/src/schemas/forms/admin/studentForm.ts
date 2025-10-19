import { ref, reactive, toRefs } from "vue";
import type { AdminStudentInfoUpdate } from "~/api/admin/admin.dto";
import type { Field } from "~/components/types/form";
import {
  ElInput,
  ElUpload,
  ElDatePicker,
  ElSelect,
  ElInputNumber,
  ElOption,
  ElInputTag,
} from "element-plus";
import { User, Message } from "@element-plus/icons-vue";

// --- Reactive form data ---

const photo_file = ref<File | null>(null);
const studentInfoFormData: AdminStudentInfoUpdate & {
  photo_file?: File | null;
} = reactive({
  student_id: "",
  full_name: "",
  first_name: "",
  last_name: "",
  birth_date: "",
  gender: "",
  grade_level: 0,
  classes: [] as string[],
  enrollment_date: "",
  address: "",
  photo_url: "",
  photo_file: null,
});

// --- Form schema ---
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
        componentProps: {
          placeholder: "Enter last name",
          suffixIcon: Message,
        },
        rules: [
          { required: true, message: "Last name required", trigger: "blur" },
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
        componentProps: {
          placeholder: "Enter address",
          suffixIcon: Message,
        },
        rules: [
          { required: true, message: "Address required", trigger: "blur" },
        ],
      },
      {
        key: "birth_date",
        label: "Birth Date",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElDatePicker,
        componentProps: {
          placeholder: "Enter birth date",
          type: "date",
          format: "YYYY-MM-DD",
          valueFormat: "YYYY-MM-DD",
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
        component: ElSelect,
        componentProps: {
          placeholder: "Enter gender",
          suffixIcon: Message,
        },
        childComponent: ElOption,
        childComponentProps: {
          options: [
            { value: "male", label: "Male" },
            { value: "female", label: "Female" },
          ],
        },
        rules: [
          { required: true, message: "Gender required", trigger: "blur" },
        ],
      },
      {
        key: "grade_level",
        label: "Grade Level",
        labelWidth: "120px",
        labelPosition: "left",
        component: ElInputNumber,
        componentProps: {
          placeholder: "Enter grade level",
          min: 1,
          max: 12,
          suffixIcon: Message,
        },
        rules: [
          { required: true, message: "Grade level required", trigger: "blur" },
          {
            type: "number",
            min: 1,
            max: 12,
            message: "Grade level must be 1-12",
            trigger: "blur",
          },
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
        component: ElInputTag,
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
        component: ElDatePicker,
        componentProps: {
          placeholder: "Enter enrollment date",
          type: "date",
          format: "YYYY-MM-DD",
          valueFormat: "YYYY-MM-DD",
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
        key: "photo_url",
        label: "Photo (Optional)",
        labelWidth: "100px",
        labelPosition: "left",
        component: ElUpload,
        componentProps: {
          listType: "picture-card",
          autoUpload: false,
          accept: "image/*",
          action: "",
        },
      },
    ],
  },
];

// --- Exports for composable ---
export const studentInfoFormDataEdit = {
  ...toRefs(studentInfoFormData),
  photo_file,
};
export const studentInfoFormSchemaEdit: Field<AdminStudentInfoUpdate>[] =
  studentInfoFormSchema;
