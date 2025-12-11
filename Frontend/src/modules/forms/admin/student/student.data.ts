import { reactive } from "vue";
import type {
  AdminCreateStudent,
  AdminUpdateStudent,
} from "~/api/admin/student/student.dto";
import { Gender } from "~/api/types/enums/gender.enum";

// ==========================================================
// 1. CREATE FORM (IAM + PROFILE)
// ==========================================================
export const getStudentFormData = (): AdminCreateStudent => ({
  username: "",
  email: "",
  password: "",
  student_id_code: "",
  first_name_kh: "",
  last_name_kh: "",
  first_name_en: "",
  last_name_en: "",
  gender: Gender.MALE,
  dob: "",
  current_grade_level: 10,
  phone_number: "",
});

export const getStudentFormDataEdit = (data?: Partial<AdminUpdateStudent>) =>
  reactive({
    student_id_code: "",
    first_name_kh: "",
    last_name_kh: "",
    first_name_en: "",
    last_name_en: "",
    gender: Gender.MALE,
    dob: "",
    current_grade_level: 10,
    phone_number: "",
    ...data,
  });
