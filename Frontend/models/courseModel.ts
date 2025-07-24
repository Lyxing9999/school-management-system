import type { Course } from "~/types/models/Course";

export class CourseModel implements Course {
  _id?: string;
  course_code: string;
  course_title: string;
  credits: number;
  department: string;
  description: string;
  created_at: string;

  constructor(data: Partial<Course> = {}) {
    this._id = data._id;
    this.course_code = data.course_code ?? "";
    this.course_title = data.course_title ?? "";
    this.credits = data.credits ?? 0;
    this.department = data.department ?? "";
    this.description = data.description ?? "";
    this.created_at = data.created_at ?? new Date().toISOString();
  }

  toDict(): Record<string, any> {
    return {
      _id: this._id,
      course_code: this.course_code,
      course_title: this.course_title,
      credits: this.credits,
      department: this.department,
      description: this.description,
      created_at: this.created_at,
    };
  }
}
