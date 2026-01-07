import type { Field } from "~/components/types/form";
import type {
  AdminCreateStudent,
  AdminUpdateStudent,
} from "~/api/admin/student/student.dto";
import { Gender } from "~/api/types/enums/gender.enum";
import {
  ElInput,
  ElDatePicker,
  ElSelect,
  ElInputNumber,
  ElOption,
} from "element-plus";
import {
  User,
  Message,
  Calendar,
  Lock,
  School,
  Iphone,
  Postcard,
} from "@element-plus/icons-vue";

export const studentFormSchema: Field<AdminCreateStudent>[] = [
  // --- ROW 1: ACCOUNT INFO (IAM) ---
  {
    row: [
      {
        key: "username",
        label: "Username",
        component: ElInput,
        componentProps: { placeholder: "e.g. student_01", suffixIcon: User },
      },
      {
        key: "email",
        label: "Email",
        component: ElInput,
        componentProps: {
          placeholder: "e.g. student01@school.com",
          suffixIcon: Message,
        },
      },
    ],
  },

  // --- ROW 2: PASSWORD & STUDENT ID ---
  {
    row: [
      {
        key: "password",
        label: "Password",
        component: ElInput,
        componentProps: {
          placeholder: "Enter a secure password",
          suffixIcon: Lock,
          type: "password",
          showPassword: true,
        },
      },
      {
        key: "student_id_code",
        label: "Student ID Code",
        component: ElInput,
        componentProps: { placeholder: "e.g. STU-0001", suffixIcon: Postcard },
      },
    ],
  },

  // --- ROW 3: KHMER NAMES ---
  {
    row: [
      {
        key: "last_name_kh",
        label: "គោត្តនាម (ខ្មែរ)",
        component: ElInput,
        componentProps: { placeholder: "បញ្ចូលគោត្តនាម", suffixIcon: User },
      },
      {
        key: "first_name_kh",
        label: "នាម (ខ្មែរ)",
        component: ElInput,
        componentProps: { placeholder: "បញ្ចូលនាម", suffixIcon: User },
      },
    ],
  },

  // --- ROW 4: ENGLISH NAMES ---
  {
    row: [
      {
        key: "last_name_en",
        label: "Last Name (EN)",
        component: ElInput,
        componentProps: { placeholder: "e.g. Sok", suffixIcon: User },
      },
      {
        key: "first_name_en",
        label: "First Name (EN)",
        component: ElInput,
        componentProps: { placeholder: "e.g. Dara", suffixIcon: User },
      },
    ],
  },

  // --- ROW 5: DEMOGRAPHICS ---
  {
    row: [
      {
        key: "gender",
        label: "Gender",
        component: ElSelect,
        componentProps: { placeholder: "Select gender" },
        childComponent: ElOption,
        childComponentProps: {
          options: [
            { value: Gender.MALE, label: "Male" },
            { value: Gender.FEMALE, label: "Female" },
          ],
        },
      },
      {
        key: "dob",
        label: "Date of Birth",
        component: ElDatePicker,
        componentProps: {
          placeholder: "YYYY-MM-DD",
          type: "date",
          format: "YYYY-MM-DD",
          valueFormat: "YYYY-MM-DD",
          suffixIcon: Calendar,
          style: { width: "100%" },
        },
      },
    ],
  },

  // --- ROW 6: ACADEMIC & CONTACT ---
  {
    row: [
      {
        key: "current_grade_level",
        label: "Grade Level",
        component: ElInputNumber,
        componentProps: {
          placeholder: "1–12",
          min: 1,
          max: 12,
          suffixIcon: School,
          style: { width: "100%" },
        },
      },
      {
        key: "phone_number",
        label: "Phone (Optional)",
        component: ElInput,
        componentProps: { placeholder: "e.g. 012345678", suffixIcon: Iphone },
      },
    ],
  },
];

// ========================================================================
// 🟠 UPDATE SCHEMA (PROFILE ONLY)
// ========================================================================

export const StudentFormSchemaEdit: Field<AdminUpdateStudent>[] = [
  // --- ROW 1: KHMER NAMES ---
  {
    row: [
      {
        key: "last_name_kh",
        label: "គោត្តនាម (ខ្មែរ)",
        component: ElInput,
        componentProps: { placeholder: "បញ្ចូលគោត្តនាម", suffixIcon: User },
      },
      {
        key: "first_name_kh",
        label: "នាម (ខ្មែរ)",
        component: ElInput,
        componentProps: { placeholder: "បញ្ចូលនាម", suffixIcon: User },
      },
    ],
  },

  // --- ROW 2: ENGLISH NAMES ---
  {
    row: [
      {
        key: "last_name_en",
        label: "Last Name (EN)",
        component: ElInput,
        componentProps: { placeholder: "e.g. Sok", suffixIcon: User },
      },
      {
        key: "first_name_en",
        label: "First Name (EN)",
        component: ElInput,
        componentProps: { placeholder: "e.g. Dara", suffixIcon: User },
      },
    ],
  },

  // --- ROW 3: DEMOGRAPHICS ---
  {
    row: [
      {
        key: "gender",
        label: "Gender",
        component: ElSelect,
        componentProps: { placeholder: "Select gender" },
        childComponent: ElOption,
        childComponentProps: {
          options: [
            { value: Gender.MALE, label: "Male" },
            { value: Gender.FEMALE, label: "Female" },
          ],
        },
      },
      {
        key: "dob",
        label: "Date of Birth",
        component: ElDatePicker,
        componentProps: {
          placeholder: "YYYY-MM-DD",
          type: "date",
          format: "YYYY-MM-DD",
          valueFormat: "YYYY-MM-DD",
          suffixIcon: Calendar,
          style: { width: "100%" },
        },
      },
    ],
  },

  // --- ROW 4: ACADEMIC & CONTACT ---
  {
    row: [
      {
        key: "current_grade_level",
        label: "Grade Level",
        component: ElInputNumber,
        componentProps: {
          placeholder: "1–12",
          min: 1,
          max: 12,
          suffixIcon: School,
          style: { width: "100%" },
        },
      },
      {
        key: "phone_number",
        label: "Phone",
        component: ElInput,
        componentProps: { placeholder: "e.g. 012345678", suffixIcon: Iphone },
      },
    ],
  },
];
