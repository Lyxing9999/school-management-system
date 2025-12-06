// ~/api/student/dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type {
  ClassSectionDTO,
  AttendanceDTO,
  GradeDTO,
  ScheduleDTO,
  AttendanceStatus,
} from "~/api/types/school.dto";

/**
 * Python: StudentClassListDTO
 */
export interface StudentClassListDTO {
  items: ClassSectionDTO[];
}

/**
 * Python: StudentAttendanceListDTO
 */
export interface StudentAttendanceListDTO {
  items: AttendanceDTO[];
}

/**
 * Python: StudentGradeListDTO
 */
export interface StudentGradeListDTO {
  items: GradeDTO[];
}

/**
 * Python: StudentScheduleListDTO
 */
export interface StudentScheduleListDTO {
  items: ScheduleDTO[];
}

/**
 * Filter DTOs (mirror Student*FilterSchema, but used as query params)
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

import type { StudentInfoBaseDataDTO } from "~/api/types/student.dto";
export type AdminUpdateStudentInfo = Partial<StudentInfoBaseDataDTO>;
