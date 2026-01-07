export type AttendanceStatus = "present" | "absent" | "excused";
export type GradeType = "exam" | "assignment"; // adjust if you have more types
import type { LifecycleDTO } from "./lifecycle.dto";
import type { Status } from "./enums/status.enum";
/**
 * Python: ClassSectionDTO
 *
 * Should match app.contexts.school.data_transfer.responses.ClassSectionDTO
 * and what Teacher/Student endpoints return.
 */
export interface ClassSectionDTO {
  id: string;
  name: string;
  homeroom_teacher_id: string | null;
  student_ids: string[];
  subject_ids: string[];
  status: Status;
  max_students: number | null;
  lifecycle: LifecycleDTO;
}

/**
 * Python: AttendanceDTO
 */
export interface AttendanceDTO {
  id: string;
  student_id: string;
  class_id: string;
  teacher_id: string;
  record_date: string;
  status: AttendanceStatus;
  lifecycle: LifecycleDTO;
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
  lifecycle: LifecycleDTO;
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
  lifecycle: LifecycleDTO;
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
  lifecycle: LifecycleDTO;
}
