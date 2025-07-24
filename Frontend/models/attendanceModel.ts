import { AttendanceStatus } from "~/types/models/Attendance"; // adjust path as needed

export class AttendanceRecordModel {
  _id?: string;
  student_id: string;
  class_id: string;
  date: string;
  status: AttendanceStatus = AttendanceStatus.PRESENT;
  recorded_by?: string;
  timestamp: string; //

  constructor(data: Partial<AttendanceRecordModel> = {}) {
    this._id = data._id;
    this.student_id = data.student_id ?? "";
    this.class_id = data.class_id ?? "";
    this.date = data.date ?? new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    this.status = data.status ?? AttendanceStatus.PRESENT;
    this.recorded_by = data.recorded_by;
    this.timestamp = data.timestamp ?? new Date().toISOString();
  }

  toDict(): Record<string, any> {
    return {
      _id: this._id,
      student_id: this.student_id,
      class_id: this.class_id,
      date: this.date,
      status: this.status,
      recorded_by: this.recorded_by,
      timestamp: this.timestamp,
    };
  }
}
