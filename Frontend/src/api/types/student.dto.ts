/**
 * @description Base Student Info
 * @example
 * {
 *  user_id: "1",
 *  student_info: {
 *    student_id: "1",
 *    full_name: "admin",
 *    photo_url: "url",
 *    photo_file: "file",
 *    first_name: "first_name",
 *    last_name: "last_name",
 *    birth_date: "birth_date",
 *    gender: "gender",
 *    grade_level: "grade_level",
 *    classes: "classes",
 *    enrollment_date: "enrollment_date",
 *    address: "address"
 *  }
 * }
 */
import { Gender } from "~/api/types/enums/gender.enum";
import { StudentStatus } from "~/api/types/enums/student-status.enum";
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
