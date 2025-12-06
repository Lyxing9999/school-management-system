import type {
  FormRegistryCreateItem,
  FormRegistryEditItem,
} from "~/form-system/types/formRegistry";

import type { TeacherMarkAttendanceDTO } from "~/api/teacher/dto";

// TODO move every Create form page to here
export type TeacherFormRegistryCreate = {
  MARK_ATTENDANCE: FormRegistryCreateItem<TeacherMarkAttendanceDTO>;
};

export type TeacherFormRegistryEdit = {};

import type { AttendanceStatus } from "~/api/types/school.dto";
export interface TeacherMarkAttendanceForm {
  student_id: string;
  class_id: string;
  status: "" | AttendanceStatus;
  record_date?: string;
}
