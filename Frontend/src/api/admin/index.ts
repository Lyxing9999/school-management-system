//api
import { UserApi } from "./user/user.api";
import { StaffApi } from "./staff/staff.api";
import { StudentApi } from "./student/student.api";
import { ClassApi } from "./class/class.api";
import { SubjectApi } from "./subject/subject.api";
import { ScheduleSlotApi } from "./schedule/schedule.api";
import { TeachingAssignmentApi } from "./teaching-assignment/teaching-assignment.api";
//service
import { UserService } from "./user/user.service";
import { StaffService } from "./staff/staff.service";
import { StudentService } from "./student/student.service";
import { ClassService } from "./class/class.service";
import { SubjectService } from "./subject/subject.service";
import { ScheduleSlotService } from "./schedule/schedule.service";
import { TeachingAssignmentService } from "./teaching-assignment/teaching-assignment.service";
/**
 * Lazy singleton pattern
 */
let _adminService: ReturnType<typeof createAdminService> | null = null;

function createAdminService() {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is undefined.");

  const adminApi = {
    user: new UserApi($api),
    staff: new StaffApi($api),
    student: new StudentApi($api),
    class: new ClassApi($api),
    subject: new SubjectApi($api),
    scheduleSlot: new ScheduleSlotApi($api),
    teachingAssignment: new TeachingAssignmentApi($api),
  };

  return {
    user: new UserService(adminApi.user),
    staff: new StaffService(adminApi.staff),
    student: new StudentService(adminApi.student),
    class: new ClassService(adminApi.class),
    subject: new SubjectService(adminApi.subject),
    scheduleSlot: new ScheduleSlotService(adminApi.scheduleSlot),
    teachingAssignment: new TeachingAssignmentService(
      adminApi.teachingAssignment
    ),
  };
}

export const adminService = () => (_adminService ??= createAdminService());
