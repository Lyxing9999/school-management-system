import type { Grade } from "~/types/models/Grade";

export class GradeModel implements Grade {
  _id?: string;
  teacher_id: string;
  student_id: string;
  student_name?: string;
  class_id: string;
  course_id?: string;

  attendance = 0;
  assignment = 0;
  quiz = 0;
  project = 0;
  midterm = 0;
  final_exam = 0;
  extra_exam = 0;

  term = "Term 1";
  remark?: string;

  created_at: string;
  updated_at?: string;

  constructor(data: Partial<Grade> = {}) {
    this._id = data._id;
    this.teacher_id = data.teacher_id ?? "";
    this.student_id = data.student_id ?? "";
    this.student_name = data.student_name;
    this.class_id = data.class_id ?? "";
    this.course_id = data.course_id;

    this.attendance = data.attendance ?? 0;
    this.assignment = data.assignment ?? 0;
    this.quiz = data.quiz ?? 0;
    this.project = data.project ?? 0;
    this.midterm = data.midterm ?? 0;
    this.final_exam = data.final_exam ?? 0;
    this.extra_exam = data.extra_exam ?? 0;

    this.term = data.term ?? "Term 1";
    this.remark = data.remark;

    this.created_at = data.created_at ?? new Date().toISOString();
    this.updated_at = data.updated_at;
  }

  get total(): number {
    return (
      (this.attendance ?? 0) +
      (this.assignment ?? 0) +
      (this.quiz ?? 0) +
      (this.project ?? 0) +
      (this.midterm ?? 0) +
      (this.final_exam ?? 0) +
      (this.extra_exam ?? 0)
    );
  }

  toDict(): Record<string, any> {
    const { total, ...rest } = this;
    return rest;
  }
}
