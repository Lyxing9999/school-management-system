export interface Grade {
  _id?: string;
  teacher_id: string;
  student_id: string;
  student_name?: string;
  class_id: string;
  course_id?: string;

  attendance?: number;
  assignment?: number;
  quiz?: number;
  project?: number;
  midterm?: number;
  final_exam?: number;
  extra_exam?: number;

  term?: string;
  remark?: string;

  created_at: string;
  updated_at?: string;

  total?: number;
}
