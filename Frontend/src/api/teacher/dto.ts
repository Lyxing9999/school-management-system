import type { ApiResponse } from "~/api/types/common/api-response.type";
import type {
  ClassSectionDTO,
  AttendanceDTO,
  GradeDTO,
  AttendanceStatus,
  GradeType,
  ScheduleDTO,
} from "~/api/types/school.dto";

import type { StudentBaseDataDTO } from "../types/student.dto";

/* ---------------------------------------------
 * Shared paging
 * ------------------------------------------- */
export interface PagedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

/* ---------------------------------------------
 * Teacher -> Students
 * ------------------------------------------- */
export interface TeacherStudentDataDTO extends StudentBaseDataDTO {}

/* ---------------------------------------------
 * Enriched Grades
 * ------------------------------------------- */
export type GradeEnriched = GradeDTO & {
  // enriched
  student_name?: string;
  student_name_en?: string;
  student_name_kh?: string;

  class_name?: string;
  subject_label?: string;
  teacher_name?: string;

  // common id echoes (some backends include these redundantly)
  student_id?: string;
  subject_id?: string;
  class_id?: string;
  teacher_id?: string;
};

/* ---------------------------------------------
 * Enriched Attendance
 * ------------------------------------------- */
export type AttendanceEnriched = AttendanceDTO & {
  // enriched
  student_name?: string;
  class_name?: string;
  teacher_name?: string;

  // optional for subject/slot attendance
  subject_id?: string;
  schedule_slot_id?: string;
  subject_label?: string;

  // optional slot pack (if backend provides)
  day_of_week?: number;
  start_time?: string;
  end_time?: string;
  room?: string;
};

/* ---------------------------------------------
 * Select DTOs (name-select)
 * These are consistent: { id, name }
 * ------------------------------------------- */
export interface TeacherStudentNameSelectDTO {
  id: string;
  name: string;
}
export interface TeacherStudentSelectNameListDTO {
  items: TeacherStudentNameSelectDTO[];
}

export interface TeacherStudentNameDTO {
  id: string;
  name: string;
}
export interface TeacherStudentNameListDTO {
  items: TeacherStudentNameDTO[];
}

export interface TeacherSubjectNameSelectDTO {
  id: string;
  name: string;
}
export interface TeacherSubjectSelectNameListDTO {
  items: TeacherSubjectNameSelectDTO[];
}

export interface TeacherClassNameSelectDTO {
  id: string;
  name: string;
}
export interface TeacherClassSelectNameListDTO {
  items: TeacherClassNameSelectDTO[];
}

/* ---------------------------------------------
 * Class list DTOs
 * ------------------------------------------- */
export interface TeacherClassListDTO {
  items: ClassSectionDTO[];
}

/* ---------------------------------------------
 * Attendance list DTOs
 * ------------------------------------------- */
export interface TeacherAttendanceListDTO {
  items: AttendanceEnriched[];
  // If you later add pagination on backend, you can extend here:
  // total?: number;
}

/* ---------------------------------------------
 * Grades paged DTO
 * ------------------------------------------- */
export type TeacherGradePagedDTO = PagedResult<GradeEnriched> & {
  // backend dump frontend
  is_homeroom?: boolean;
  can_edit?: boolean;
};

/* ---------------------------------------------
 * Request DTOs
 * mirror app.contexts.teacher.data_transfer.requests.*
 * ------------------------------------------- */
export interface TeacherMarkAttendanceDTO {
  student_id: string;
  class_id: string;

  // REQUIRED by backend
  subject_id: string;
  schedule_slot_id: string;

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

/* ---------------------------------------------
 * Schedule DTOs (enriched)
 * ------------------------------------------- */
export interface TeacherScheduleDTO extends ScheduleDTO {
  class_name?: string;

  subject_id?: string;
  subject_label?: string;

  teacher_name?: string;

  // optional UI convenience
  day_label?: string;
}

export interface TeacherScheduleListDTO {
  items: TeacherScheduleDTO[];
  total: number;
  page: number;
  page_size: number;
}

/* ---------------------------------------------
 * Class summary DTOs
 * ------------------------------------------- */
export interface TeacherClassSummaryDTO {
  total_classes: number;
  total_students: number;
  total_subjects: number;
}

export interface TeacherClassListWithSummeryDTO {
  items: ClassSectionDTO[];
  summary: TeacherClassSummaryDTO;
}

/* ---------------------------------------------
 * Mutations: soft delete / restore
 * ------------------------------------------- */
export interface TeacherSoftDeleteResultDTO {
  modified_count: number;
  deleted: boolean;
}

export interface TeacherRestoreResultDTO {
  modified_count: number;
  restored: boolean;
}

/* ---------------------------------------------
 * Schedule Slot Select (Attendance needs both:
 * schedule_slot_id + subject_id)
 * ------------------------------------------- */
export interface TeacherScheduleSlotSelectDTO {
  value: string; // schedule_slot_id
  label: string; // "07:30–08:15 • Math (Room A)"

  subject_id?: string;
  subject_label?: string;

  class_id?: string;
  day_of_week?: number;
  start_time?: string;
  end_time?: string;
  room?: string;
}

export interface TeacherScheduleSlotSelectListDTO {
  items: TeacherScheduleSlotSelectDTO[];
}

export type TeacherScheduleSlotSelectListResponse =
  ApiResponse<TeacherScheduleSlotSelectListDTO>;
/* ---------------------------------------------
 * Wrapped responses
 * ------------------------------------------- */
export type TeacherGetClassesResponse = ApiResponse<TeacherClassListDTO>;
export type TeacherClassListWithSummeryResponse =
  ApiResponse<TeacherClassListWithSummeryDTO>;

export type TeacherClassSelectNameListResponse =
  ApiResponse<TeacherClassSelectNameListDTO>;
export type TeacherStudentsSelectNameListResponse =
  ApiResponse<TeacherStudentSelectNameListDTO>;
export type TeacherStudentNameListResponse =
  ApiResponse<TeacherStudentNameListDTO>;
export type TeacherSubjectsSelectNameListResponse =
  ApiResponse<TeacherSubjectSelectNameListDTO>;

export type TeacherMarkAttendanceResponse = ApiResponse<AttendanceDTO>;
export type TeacherChangeAttendanceStatusResponse = ApiResponse<AttendanceDTO>;
export type TeacherListClassAttendanceResponse =
  ApiResponse<TeacherAttendanceListDTO>;

export type TeacherAddGradeResponse = ApiResponse<GradeDTO>;
export type TeacherUpdateGradeScoreResponse = ApiResponse<GradeDTO>;
export type TeacherChangeGradeTypeResponse = ApiResponse<GradeDTO>;
export type TeacherListClassGradesResponse = ApiResponse<TeacherGradePagedDTO>;

export type TeacherListMyScheduleResponse = ApiResponse<TeacherScheduleListDTO>;

export type TeacherSoftDeleteAttendanceResponse =
  ApiResponse<TeacherSoftDeleteResultDTO>;
export type TeacherRestoreAttendanceResponse =
  ApiResponse<TeacherRestoreResultDTO>;

export type TeacherSoftDeleteGradeResponse =
  ApiResponse<TeacherSoftDeleteResultDTO>;
export type TeacherRestoreGradeResponse = ApiResponse<TeacherRestoreResultDTO>;

export type TeacherStudentDataResponse = ApiResponse<TeacherStudentDataDTO>;
