import { adminService } from "~/api/admin";
import type { UseFormService } from "~/forms/types/serviceFormTypes";

import type { AdminUpdateStudentInfo } from "~/api/admin/student/dto";
export function useServiceFormStudentInfo(): UseFormService<
  any,
  AdminUpdateStudentInfo
> {
  const adminApiService = adminService();

  return {
    update: (id, data) => adminApiService.student.updateStudentInfo(id, data),
    getDetail: (id) => adminApiService.student.getStudentInfo(id),
  };
}
