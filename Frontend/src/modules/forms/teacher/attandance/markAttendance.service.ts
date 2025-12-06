import type { UseFormService } from "~/form-system/types/serviceFormTypes";
import type {
  TeacherMarkAttendanceDTO,
  TeacherChangeAttendanceStatusDTO,
} from "~/api/teacher/dto";
import { teacherService } from "~/api/teacher";
import type { ScheduleDTO } from "~/api/types/school.dto";

export function useServiceFormAttendance(): UseFormService<
  TeacherMarkAttendanceDTO,
  TeacherChangeAttendanceStatusDTO,
  boolean,
  ScheduleDTO,
  ScheduleDTO,
  ScheduleDTO
> {
  const service = teacherService();

  return {
    create: async (data) => {
      await service.teacher.markAttendance(data);
    },
    update: async (id, data) => {
      await service.teacher.changeAttendanceStatus(id, data);
    },
  };
}
