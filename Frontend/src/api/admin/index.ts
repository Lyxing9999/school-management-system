// ~/api/admin/index.ts
import { UserApi } from "./user/api";
import { StaffApi } from "./staff/api";
import { StudentApi } from "./student/api";
import { ClassApi } from "./class/api";
import { SubjectApi } from "./subject/api";

import { UserService } from "./user/service";
import { StaffService } from "./staff/service";
import { StudentService } from "./student/service";
import { ClassService } from "./class/service";
import { SubjectService } from "./subject/service";

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
  };

  return {
    user: new UserService(adminApi.user),
    staff: new StaffService(adminApi.staff),
    student: new StudentService(adminApi.student),
    class: new ClassService(adminApi.class),
    subject: new SubjectService(adminApi.subject),
  };
}

export const adminService = () => (_adminService ??= createAdminService());
