// ~/api/teacher/dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";
import type {
  ClassSectionDTO,
  AttendanceDTO,
  GradeDTO,
  AttendanceStatus,
  GradeType,
} from "~/api/types/school.dto";

/**
 * Python: TeacherClassListDTO
 */
export interface TeacherClassListDTO {
  items: ClassSectionDTO[];
}

/**
 * Python: TeacherAttendanceListDTO
 */
export interface TeacherAttendanceListDTO {
  items: AttendanceDTO[];
}

/**
 * Python: TeacherGradeListDTO
 */
export interface TeacherGradeListDTO {
  items: GradeDTO[];
}

/**
 * Request DTOs
 * mirror app.contexts.teacher.data_transfer.requests.*
 */

export interface TeacherMarkAttendanceDTO {
  student_id: string;
  class_id: string;
  status: AttendanceStatus;
  record_date?: string; // "YYYY-MM-DD"
}

export interface TeacherChangeAttendanceStatusDTO {
  new_status: AttendanceStatus;
}

export interface TeacherAddGradeDTO {
  student_id: string;
  subject_id: string;
  class_id?: string | null;
  score: number;
  type: GradeType;
  term?: string | null;
}

export interface TeacherUpdateGradeScoreDTO {
  score: number;
}

export interface TeacherChangeGradeTypeDTO {
  type: GradeType;
}

/**
 * Wrapped responses
 */
export type TeacherGetClassesResponse = ApiResponse<TeacherClassListDTO>;
export type TeacherMarkAttendanceResponse = ApiResponse<AttendanceDTO>;
export type TeacherChangeAttendanceStatusResponse = ApiResponse<AttendanceDTO>;
export type TeacherAddGradeResponse = ApiResponse<GradeDTO>;
export type TeacherUpdateGradeScoreResponse = ApiResponse<GradeDTO>;
export type TeacherChangeGradeTypeResponse = ApiResponse<GradeDTO>;
export type TeacherListClassAttendanceResponse =
  ApiResponse<TeacherAttendanceListDTO>;
export type TeacherListClassGradesResponse = ApiResponse<TeacherGradeListDTO>;
