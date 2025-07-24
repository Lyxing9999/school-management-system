import type { ScheduleItem } from "~/types/models/Schedule";

export class ClassInfoModel {
  course_code: string = "";
  course_title: string = "";
  lecturer: string = "";
  email?: string;
  phone_number: string = "";
  hybrid: boolean = false;
  schedule?: ScheduleItem[];
  credits: number = 0;
  link_telegram?: string;
  department: string = "";
  description?: string;
  year: number = new Date().getFullYear();

  constructor(data: Partial<ClassInfoModel> = {}) {
    Object.assign(this, {
      course_code: "",
      course_title: "",
      lecturer: "",
      phone_number: "",
      hybrid: false,
      credits: 0,
      department: "",
      description: "",
      year: new Date().getFullYear(),
      ...data,
    });
  }

  static empty(): ClassInfoModel {
    return new ClassInfoModel();
  }

  toDict(): Record<string, any> {
    return {
      course_code: this.course_code,
      course_title: this.course_title,
      lecturer: this.lecturer,
      email: this.email,
      phone_number: this.phone_number,
      hybrid: this.hybrid,
      schedule: this.schedule,
      credits: this.credits,
      link_telegram: this.link_telegram,
      department: this.department,
      description: this.description,
      year: this.year,
    };
  }
}

export class ClassModel {
  _id?: string;
  class_info?: ClassInfoModel;
  created_by?: string;
  students_enrolled: string[] = [];
  max_students: number = 30;

  constructor(data: Partial<ClassModel> = {}) {
    Object.assign(this, {
      students_enrolled: [],
      max_students: 30,
      ...data,
    });

    this.class_info = data.class_info
      ? new ClassInfoModel(data.class_info)
      : undefined;
  }

  static empty(): ClassModel {
    return new ClassModel({
      class_info: ClassInfoModel.empty(),
    });
  }

  toDict(): Record<string, any> {
    return {
      _id: this._id,
      class_info: this.class_info?.toDict(),
      created_by: this.created_by,
      students_enrolled: this.students_enrolled,
      max_students: this.max_students,
    };
  }
}
