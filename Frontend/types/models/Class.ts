import type { ScheduleItem } from "./Schedule";

export interface ClassInfo {
  course_code: string;
  course_title: string;
  lecturer: string;
  email?: string;
  phone_number: string;
  hybrid?: boolean;
  schedule?: ScheduleItem[];
  credits?: number;
  department?: string;
  description?: string;
  year?: number;
}

export interface ClassModel {
  _id?: string;
  class_id: string;
  class_info: ClassInfo;
  students_enrolled: string[];
  max_students?: number;
  created_at: string;
  update_history: string[];
}
