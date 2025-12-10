// ~/api/admin/dashboard/dashboard.dto.ts
import type { ApiResponse } from "~/api/types/common/api-response.type";

// ---------- Overview ----------

export interface AdminOverviewDTO {
  total_students: number;
  total_teachers: number;
  total_classes: number;
  total_subjects: number;
  today_lessons: number;
}

// ---------- Attendance ----------

export interface AdminAttendanceStatusSummaryDTO {
  status: string; // "present" | "absent" | "excused" | ...
  count: number;
}

export interface AdminAttendanceDailyTrendDTO {
  date: string; // "YYYY-MM-DD"
  present: number;
  absent: number;
  excused: number;
  total: number;
}

export interface AdminAttendanceByClassDTO {
  class_id: string;
  class_name: string;
  present: number;
  absent: number;
  excused: number;
  total: number;
}

export interface AdminTopAbsentStudentDTO {
  student_id: string;
  student_name: string;
  class_id: string;
  class_name: string;
  absent_count: number;
  total_records: number;
}

export interface AdminAttendanceDashboardDTO {
  status_summary: AdminAttendanceStatusSummaryDTO[];
  daily_trend: AdminAttendanceDailyTrendDTO[];
  by_class: AdminAttendanceByClassDTO[];
  top_absent_students: AdminTopAbsentStudentDTO[];
}

// ---------- Grades ----------

export interface AdminAvgScoreBySubjectDTO {
  subject_id: string;
  subject_name: string;
  avg_score: number;
  sample_size: number;
}

export interface AdminGradeDistributionBucketDTO {
  range: string; // "0-49", "50-69", ...
  count: number;
}

export interface AdminPassRateByClassDTO {
  class_id: string;
  class_name: string;
  avg_score: number;
  pass_rate: number; // 0..1
  total_students: number;
  passed: number;
}

export interface AdminGradeDashboardDTO {
  avg_score_by_subject: AdminAvgScoreBySubjectDTO[];
  grade_distribution: AdminGradeDistributionBucketDTO[];
  pass_rate_by_class: AdminPassRateByClassDTO[];
}

// ---------- Schedule ----------

export interface AdminLessonsByWeekdayDTO {
  day_of_week: number; // 1=Mon..7=Sun
  label: string; // "Mon", "Tue", ...
  lessons: number;
}

export interface AdminLessonsByTeacherDTO {
  teacher_id: string;
  teacher_name: string;
  lessons: number;
  classes: number;
}

export interface AdminScheduleDashboardDTO {
  lessons_by_weekday: AdminLessonsByWeekdayDTO[];
  lessons_by_teacher: AdminLessonsByTeacherDTO[];
}

// ---------- Root dashboard ----------

export interface AdminDashboardDTO {
  overview: AdminOverviewDTO;
  attendance: AdminAttendanceDashboardDTO;
  grades: AdminGradeDashboardDTO;
  schedule: AdminScheduleDashboardDTO;
}

export type AdminDashboardResponse = ApiResponse<AdminDashboardDTO>;

// ---------- Filters (for query params) ----------

export interface AdminDashboardFilterDTO {
  /**
   * ISO date string: "YYYY-MM-DD"
   * Backend will parse and use as date_from in aggregations.
   */
  date_from?: string;

  /**
   * ISO date string: "YYYY-MM-DD"
   * Backend will parse and use as date_to in aggregations.
   */
  date_to?: string;

  /**
   * Term, must match what you store in GradeRecord.term
   * Example: "S1", "S2", "SUMMER"
   */
  term?: string;
}
