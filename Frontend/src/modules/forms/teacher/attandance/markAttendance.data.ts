import type { TeacherMarkAttendanceForm } from "../types";

const todayISO = new Date().toISOString().slice(0, 10);

export const getAttendanceFormData = (): TeacherMarkAttendanceForm => ({
  student_id: "",
  class_id: "",
  status: "",
  record_date: todayISO,
});
