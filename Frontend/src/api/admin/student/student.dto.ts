import type { ApiResponse } from "~/api/types/common/api-response.type";
import { Gender } from "~/api/types/enums/gender.enum"; // សូមប្រាកដថាមាន Enum នេះ
import { StudentStatus } from "~/api/types/enums/student-status.enum"; // សូមប្រាកដថាមាន Enum នេះ (Optional)

export type AdminApiResponse<T> = ApiResponse<T>;

/* --------------------------------------------------------
   BASE DATA (Matches Backend StudentBaseDataDTO)
-------------------------------------------------------- */
export interface StudentBaseDataDTO {
  id: string; // ObjectId string
  user_id: string; // IAM ID
  student_id_code: string;

  first_name_kh: string;
  last_name_kh: string;
  first_name_en: string;
  last_name_en: string;

  gender: Gender;
  dob: string; // ISO Date String or 'YYYY-MM-DD'
  current_grade_level: number;

  photo_url?: string;
  phone_number?: string;

  status: StudentStatus | string;

  created_at: string;
  updated_at: string;
}

/* --------------------------------------------------------
   READ OPERATIONS (GET)
-------------------------------------------------------- */

export interface AdminGetStudentData extends StudentBaseDataDTO {
  username?: string;
  email?: string;
}

export interface AdminGetStudentItemData extends AdminGetStudentData {}

export interface AdminGetPageStudentData {
  students: AdminGetStudentItemData[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

/* --------------------------------------------------------
   WRITE OPERATIONS (CREATE/UPDATE)
-------------------------------------------------------- */
export interface AdminCreateStudent {
  // --- IAM Part ---
  username: string;
  email: string;
  password: string;

  // --- Profile Part ---
  student_id_code: string;
  first_name_kh: string;
  last_name_kh: string;
  first_name_en: string;
  last_name_en: string;
  gender: Gender;
  dob: string;
  current_grade_level: number;

  phone_number?: string;
}

// Update only updates Profile info (Password/Email update uses User API)
export interface AdminUpdateStudent {
  first_name_kh?: string;
  last_name_kh?: string;
  first_name_en?: string;
  last_name_en?: string;
  gender?: Gender;
  dob?: string;
  current_grade_level?: number;
  phone_number?: string;
  status?: StudentStatus;
}

/* --------------------------------------------------------
   SELECT / DROPDOWN OPTIONS
-------------------------------------------------------- */

export interface AdminStudentNameSelectDTO {
  value: string;
  label: string;

  first_name_kh?: string | null;
  last_name_kh?: string | null;
  first_name_en?: string | null;
  last_name_en?: string | null;
  full_name_kh?: string | null;
  full_name_en?: string | null;
}

export interface AdminStudentListSelectDTO {
  items: AdminStudentNameSelectDTO[];
}

/* --------------------------------------------------------
   RESPONSE TYPES
-------------------------------------------------------- */
export type AdminGetStudentResponse = AdminApiResponse<AdminGetStudentData>;
export type AdminCreateStudentResponse = AdminApiResponse<AdminGetStudentData>;
export type AdminGetPageStudentResponse =
  AdminApiResponse<AdminGetPageStudentData>;
export type AdminStudentListSelectResponse =
  AdminApiResponse<AdminStudentListSelectDTO>;
export type StudentBaseDataResponse = AdminApiResponse<StudentBaseDataDTO>;
export type AdminStudentNameSelectResponse =
  AdminApiResponse<AdminStudentNameSelectDTO>;
