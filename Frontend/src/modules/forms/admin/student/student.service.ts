import { adminService } from "~/api/admin";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";

import type {
  AdminCreateStudent,
  StudentBaseDataDTO,
  AdminUpdateStudent,
} from "~/api/admin/student/student.dto";
export function useServiceFormStudent(): UseFormService<
  AdminCreateStudent,
  AdminUpdateStudent,
  boolean,
  StudentBaseDataDTO,
  StudentBaseDataDTO,
  StudentBaseDataDTO
> {
  const adminApiService = adminService();

  return {
    create: (data) =>
      adminApiService.student.createStudent(data, { showSuccess: true }),
    update: (id, data) =>
      adminApiService.student.updateStudentUserId(id, data, {
        showSuccess: true,
      }),
    getDetail: (id) => adminApiService.student.getStudentUserId(id),
  };
}
