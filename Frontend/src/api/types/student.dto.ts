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

export interface StudentInfoBaseDataDTO {
  user_id: string;
  student_info: {
    student_id: string;
    full_name: string;
    photo_url: string | null | undefined;
    photo_file?: File | null;
    first_name?: string;
    last_name?: string;
    birth_date?: string;
    gender?: string;
    grade_level?: number;
    classes?: string[];
    enrollment_date?: string;
    address?: string;
  };
}

