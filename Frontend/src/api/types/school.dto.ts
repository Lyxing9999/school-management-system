// ~/api/school/dto.ts
export type AttendanceStatus = "present" | "absent" | "excused";
export type GradeType = "exam" | "assignment"; // adjust if you have more types

/**
 * Python: ClassSectionDTO
 *
 * Should match app.contexts.school.data_transfer.responses.ClassSectionDTO
 * and what Teacher/Student endpoints return.
 */
export interface ClassSectionDTO {
  id: string;
  name: string;
  teacher_id: string | null;
  student_ids: string[];
  subject_ids: string[];
  max_students: number | null;
  created_at?: string; // ISO datetime (optional if backend doesn’t include)
  updated_at?: string; // ISO datetime
}

/**
 * Python: AttendanceDTO
 */
export interface AttendanceDTO {
  id: string;
  student_id: string;
  class_id: string;
  teacher_id: string;
  date: string; // ISO date (YYYY-MM-DD)
  status: AttendanceStatus;
}

/**
 * Python: GradeDTO
 */
export interface GradeDTO {
  id: string;
  student_id: string;
  subject_id: string;
  teacher_id: string;
  class_id: string | null;
  term: string | null;
  score: number;
  type: GradeType;
}

/**
 * Python: ScheduleDTO
 */
export interface ScheduleDTO {
  id: string;
  class_id: string;
  teacher_id: string;
  day_of_week: number; // 1–7
  start_time: string; // "HH:MM:SS" or ISO time
  end_time: string;
  room: string | null;
}

/**
 * Python: SubjectDTO
 */
export interface SubjectDTO {
  id: string;
  name: string;
  code: string;
  description: string | null;
  allowed_grade_levels: number[] | null;
  is_active: boolean;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
