import { markAttendanceForm } from "~/modules/forms/teacher";

import type {
  TeacherFormRegistryCreate,
  TeacherFormRegistryEdit,
} from "~/modules/forms/teacher/types";








export const teacherFormRegistryCreate: TeacherFormRegistryCreate = {
  MARK_ATTENDANCE: {
    service: () => markAttendanceForm.useServiceFormAttendance(),
    schema: markAttendanceForm.useAttendanceFormSchema,
    formData: () => markAttendanceForm.getAttendanceFormData(),
  },
};




export const teacherFormRegistryEdit: TeacherFormRegistryEdit = {
  MARK_ATTENDANCE: {
    service: () => markAttendanceForm.useServiceFormAttendance(),
    schema: markAttendanceForm.useAttendanceFormSchema,
    formData: () => markAttendanceForm.getAttendanceFormData(),
  },
};
