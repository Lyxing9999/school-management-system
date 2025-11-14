import { ref, reactive, toRefs } from "vue";
import type { AdminCreateStudentInfo } from "~/api/admin/student/dto";
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

export const studentInfoFormSchema: Field<AdminCreateStudentInfo>[] = [
  {
    row: [
      {
        key: "student_id",
        label: "Student ID",

        component: ElInput,
        componentProps: { placeholder: "Enter student id", suffixIcon: User },
      },
      {
        key: "full_name",
        label: "Full Name",
        component: ElInput,
        componentProps: { placeholder: "Enter full name", suffixIcon: Message },
      },
    ],
  },
  {
    row: [
      {
        key: "first_name",
        label: "First Name",
        component: ElInput,
        componentProps: {
          placeholder: "Enter first name",
          suffixIcon: Message,
        },
      },
      {
        key: "last_name",
        label: "Last Name",

        component: ElInput,
        componentProps: {
          placeholder: "Enter last name",
          suffixIcon: Message,
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
          suffixIcon: Message,
        },
      },
      {
        key: "birth_date",
        label: "Birth Date",

        component: ElDatePicker,
        componentProps: {
          placeholder: "Enter birth date",
          type: "date",
          format: "YYYY-MM-DD",
          valueFormat: "YYYY-MM-DD",
          suffixIcon: Message,
        },
      },
    ],
  },
  {
    row: [
      {
        key: "gender",
        label: "Gender",
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
      },
      {
        key: "grade_level",
        label: "Grade Level",
        component: ElInputNumber,
        componentProps: {
          placeholder: "Enter grade level",
          min: 1,
          max: 12,
          suffixIcon: Message,
        },
      },
    ],
  },
  {
    row: [
      {
        key: "classes",
        label: "Classes",
        component: ElInputTag,
        componentProps: { placeholder: "Enter classes", suffixIcon: Message },
      },
      {
        key: "enrollment_date",
        label: "Enrollment Date",

        component: ElDatePicker,
        componentProps: {
          placeholder: "Enter enrollment date",
          type: "date",
          format: "YYYY-MM-DD",
          valueFormat: "YYYY-MM-DD",
          suffixIcon: Message,
        },
      },
    ],
  },
  {
    row: [
      {
        key: "photo_url",
        label: "Photo (Optional)",
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

export const studentInfoFormSchemaEdit: Field<AdminCreateStudentInfo>[] =
  studentInfoFormSchema;
