// ~/api/student/student.dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { AttendanceStatus, GradeType } from "~/api/types/school.dto"; // keep enums here if you already have them

interface LifecycleDTO {
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

/**
 * Mirrors Python: StudentClassSectionDTO extends ClassSectionDTO
 * Student-specific additions:
 * - student_count
 * - subject_count
 * - teacher_name
 * - subject_labels
 */
export interface StudentClassSectionDTO {
  id: string;
  name: string;

  teacher_id?: string | null;
  teacher_name: string;

  subject_ids: string[];
  subject_labels: string[];

  enrolled_count: number;
  max_students: number;

  // Python: ClassSectionStatus (string enum usually)
  status: string;

  student_count: number;
  subject_count: number;

  lifecycle: LifecycleDTO;
}

/**
 * Mirrors Python: StudentScheduleDTO
 * NOTE: Python does NOT include subject_label, but your UI can safely treat it as optional
 * if the backend later returns it.
 */
export interface StudentScheduleDTO {
  id: string;

  student_id?: string | null;
  class_id?: string | null;
  subject_id?: string | null;

  day_of_week: number; // 1..7
  start_time: string; // "HH:mm"
  end_time: string; // "HH:mm"

  class_name?: string | null;
  teacher_name?: string | null;
  room?: string | null;

  // optional convenience (not required by backend)
  subject_label?: string | null;

  lifecycle: LifecycleDTO;
}

/**
 * Mirrors Python: StudentAttendanceDTO
 */
export interface StudentAttendanceDTO {
  id: string;
  student_id: string;
  student_name?: string | null;

  class_id?: string | null;
  class_name?: string | null;

  status: AttendanceStatus;
  record_date: string; // "YYYY-MM-DD" or ISO date (backend sends date)

  marked_by_teacher_id: string;
  teacher_name?: string | null;

  lifecycle: LifecycleDTO;
}

/**
 * Mirrors Python: StudentGradeDTO
 */
export interface StudentGradeDTO {
  id: string;

  student_id: string;
  student_name?: string | null;

  class_id?: string | null;
  class_name?: string | null;

  subject_id: string;
  subject_label?: string | null;

  score: number;
  type: GradeType;
  term?: string | null;

  lifecycle: LifecycleDTO;
}

/**
 * List DTOs (Python: Student*ListDTO)
 */
export interface StudentClassListDTO {
  items: StudentClassSectionDTO[];
}

export interface StudentScheduleListDTO {
  items: StudentScheduleDTO[];
}

export interface StudentAttendanceListDTO {
  items: StudentAttendanceDTO[];
}

export interface StudentGradeListDTO {
  items: StudentGradeDTO[];
}

/**
 * Filter DTOs (query params)
 * Your existing TS uses from_date/to_date — keep that.
 */
export interface StudentAttendanceFilterDTO {
  class_id?: string;
  status?: AttendanceStatus;
  from_date?: string; // "YYYY-MM-DD"
  to_date?: string; // "YYYY-MM-DD"
}

export interface StudentGradesFilterDTO {
  class_id?: string;
  subject_id?: string;
  term?: string;
}

export interface StudentScheduleFilterDTO {
  day_of_week?: number; // 1–7
  class_id?: string;
}

/**
 * Wrapped responses (wrap_response)
 */
export type StudentGetClassesResponse = ApiResponse<StudentClassListDTO>;
export type StudentGetAttendanceResponse =
  ApiResponse<StudentAttendanceListDTO>;
export type StudentGetGradesResponse = ApiResponse<StudentGradeListDTO>;
export type StudentGetScheduleResponse = ApiResponse<StudentScheduleListDTO>;
