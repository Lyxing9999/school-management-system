// ~/api/student/student.dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { AttendanceStatus, GradeType } from "~/api/types/school.dto";

export interface LifecycleDTO {
  created_at: string;
  updated_at: string;
  deleted_at?: string | null;
  deleted_by?: string | null;
}

/* ---------------------------------------------
 * Student Classes
 * ------------------------------------------- */
export interface StudentClassSectionDTO {
  id: string;
  name: string;

  homeroom_teacher_id?: string | null;
  homeroom_teacher_name: string;

  subject_ids: string[];
  subject_labels: string[];

  enrolled_count: number;
  max_students: number;

  status: string;

  student_count: number;
  subject_count: number;

  lifecycle: LifecycleDTO;
}

export interface StudentClassListDTO {
  items: StudentClassSectionDTO[];
}

/* ---------------------------------------------
 * Student Schedule
 * ------------------------------------------- */
export interface StudentScheduleDTO {
  id: string;

  student_id?: string | null;
  class_id?: string | null;
  subject_id?: string | null;

  day_of_week: number;
  start_time: string;
  end_time: string;

  class_name?: string | null;
  teacher_name?: string | null;
  room?: string | null;

  subject_label?: string | null;

  lifecycle: LifecycleDTO;
}

export interface StudentScheduleListDTO {
  items: StudentScheduleDTO[];
}

/* ---------------------------------------------
 * Student Attendance
 * ------------------------------------------- */
export interface StudentAttendanceDTO {
  id: string;

  student_id: string;
  student_name?: string | null;

  class_id?: string | null;
  class_name?: string | null;

  subject_id?: string | null;
  subject_label?: string | null;

  schedule_slot_id?: string | null;
  day_of_week?: number | null;
  start_time?: string | null;
  end_time?: string | null;
  room?: string | null;

  status: AttendanceStatus;
  record_date: string;

  marked_by_teacher_id?: string | null;
  teacher_name?: string | null;

  lifecycle: LifecycleDTO;
}
export interface StudentAttendanceListDTO {
  items: StudentAttendanceDTO[];
}

/* ---------------------------------------------
 * Student Grades
 * ------------------------------------------- */
export interface StudentGradeDTO {
  id: string;

  student_id: string;
  student_name?: string | null;

  class_id?: string | null;
  class_name?: string | null;

  subject_id: string;
  subject_label?: string | null;

  score: number;
  type: GradeType; // "exam" | "quiz" | "assignment" (from your enum)
  term?: string | null;

  lifecycle: LifecycleDTO;
}

/** Old (non-paged) list (keep if used elsewhere) */
export interface StudentGradeListDTO {
  items: StudentGradeDTO[];
}

/** NEW: paged response (matches backend) */
export interface StudentGradePagedDTO {
  items: StudentGradeDTO[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

/* ---------------------------------------------
 * Filters
 * ------------------------------------------- */
export interface StudentAttendanceFilterDTO {
  class_id?: string;
  status?: AttendanceStatus;
  from_date?: string;
  to_date?: string;
}

export interface StudentGradesFilterDTO {
  class_id?: string;
  subject_id?: string;

  term?: string;
  page?: number;
  page_size?: number;
}
export interface StudentScheduleFilterDTO {
  day_of_week?: number;
  class_id?: string;
}

/* ---------------------------------------------
 * Wrapped responses (wrap_response)
 * ------------------------------------------- */
export type StudentGetClassesResponse = ApiResponse<StudentClassListDTO>;
export type StudentGetAttendanceResponse =
  ApiResponse<StudentAttendanceListDTO>;
export type StudentGetScheduleResponse = ApiResponse<StudentScheduleListDTO>;

/** IMPORTANT: update grades response to paged */
export type StudentGetGradesResponse = ApiResponse<StudentGradePagedDTO>;
