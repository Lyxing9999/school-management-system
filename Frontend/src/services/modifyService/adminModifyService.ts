import type { UseModifyService } from "~/services/types";
import type {
  AdminAssignTeacher,
  AdminAssignStudent,
  AdminUnassignTeacher,
  AdminUnassignStudent,
} from "~/api/admin/admin.dto";
import { AdminService } from "~/services/adminService";
import { AdminApi } from "~/api/admin/admin.api";
import type { BaseClassDataDTO } from "~/api/types/baseClass";

const getAdminService = () => {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is not initialized");
  return new AdminService(new AdminApi($api));
};
export interface UseClassModifyService
  extends UseModifyService<
    AdminAssignTeacher | AdminAssignStudent,
    AdminUnassignTeacher | AdminUnassignStudent,
    BaseClassDataDTO
  > {
  assignTeacher: (
    id: string,
    data: AdminAssignTeacher
  ) => Promise<BaseClassDataDTO>;
  unassignTeacher: (id: string) => Promise<BaseClassDataDTO>;
  assignStudent: (
    id: string,
    data: AdminAssignStudent
  ) => Promise<BaseClassDataDTO>;
  removeStudent: (
    id: string,
    data: AdminUnassignStudent
  ) => Promise<BaseClassDataDTO>;
}
export const serviceClassModify: UseClassModifyService = {
  assignTeacher: (id: string, data: AdminAssignTeacher) =>
    getAdminService().assignTeacher(id, data),

  unassignTeacher: (id: string) => getAdminService().unassignTeacher(id),

  assignStudent: (id: string, data: AdminAssignStudent) =>
    getAdminService().assignStudent(id, data),

  removeStudent: (id: string, data: AdminUnassignStudent) =>
    getAdminService().removeStudent(id, data),
};
