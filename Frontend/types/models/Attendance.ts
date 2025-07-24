export enum AttendanceStatus {
  PRESENT = "present",
  ABSENT = "absent",
  LAET = "late",
  EXCUSED = "excused",
}
export interface AttendanceRecord {
  student_id: string;
  class_id: string;
  date: string;
  status: AttendanceStatus;
  recorded_by?: string;
  timestamp?: string;
}
