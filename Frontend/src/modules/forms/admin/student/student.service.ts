import { adminService } from "~/api/admin";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";

import type { AdminCreateStudent } from "~/api/admin/student/student.dto";
export function useServiceFormStudent(): UseFormService<
  any,
  AdminCreateStudent
> {
  const adminApiService = adminService();

  return {
    create: (data) =>
      adminApiService.student.createStudent(data, { showSuccess: true }),
  };
}
