import type { Field } from "~/components/types/form";
import type {
  AdminCreateStudent,
  AdminUpdateStudent,
} from "~/api/admin/student/student.dto";
import { Gender } from "~/api/types/enums/gender.enum"; // Make sure you have this
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
        componentProps: { placeholder: "k.bunly", suffixIcon: User },
      },
      {
        key: "email",
        label: "Email",
        component: ElInput,
        componentProps: {
          placeholder: "example@school.com",
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
          placeholder: "******",
          suffixIcon: Lock,
          type: "password",
          showPassword: true,
        },
      },
      {
        key: "student_id_code",
        label: "Student ID Code",
        component: ElInput,
        componentProps: { placeholder: "STU-001", suffixIcon: Postcard },
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
        componentProps: { placeholder: "កាំង", suffixIcon: User },
      },
      {
        key: "first_name_kh",
        label: "នាម (ខ្មែរ)",
        component: ElInput,
        componentProps: { placeholder: "ប៊ុនលី", suffixIcon: User },
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
        componentProps: { placeholder: "Kaing", suffixIcon: User },
      },
      {
        key: "first_name_en",
        label: "First Name (EN)",
        component: ElInput,
        componentProps: { placeholder: "Bunly", suffixIcon: User },
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
        componentProps: { placeholder: "Select Gender" },
        // Define Options manually or map from Enum
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
          placeholder: "Select date",
          type: "date",
          format: "YYYY-MM-DD",
          valueFormat: "YYYY-MM-DD", // Must match Backend Pydantic validation
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
          placeholder: "Grade",
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
        componentProps: { placeholder: "012...", suffixIcon: Iphone },
      },
    ],
  },
];

// ========================================================================
// 🟠 UPDATE SCHEMA (PROFILE ONLY)
// ========================================================================
// We exclude Username/Password/Email/StudentCode because usually
// these are handled separately or read-only in basic edit.

export const StudentFormSchemaEdit: Field<AdminUpdateStudent>[] = [
  // --- ROW 1: KHMER NAMES ---
  {
    row: [
      {
        key: "last_name_kh",
        label: "គោត្តនាម (ខ្មែរ)",
        component: ElInput,
        componentProps: { placeholder: "កាំង", suffixIcon: User },
      },
      {
        key: "first_name_kh",
        label: "នាម (ខ្មែរ)",
        component: ElInput,
        componentProps: { placeholder: "ប៊ុនលី", suffixIcon: User },
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
        componentProps: { placeholder: "Kaing", suffixIcon: User },
      },
      {
        key: "first_name_en",
        label: "First Name (EN)",
        component: ElInput,
        componentProps: { placeholder: "Bunly", suffixIcon: User },
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
        componentProps: { placeholder: "Select Gender" },
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
        componentProps: { placeholder: "012...", suffixIcon: Iphone },
      },
    ],
  },
];
