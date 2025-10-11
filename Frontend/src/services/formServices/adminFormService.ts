// ~/services/formServices/adminFormService.ts
import type { UseFormService } from "~/services/types";
import type {
  AdminCreateUser,
  AdminUpdateUsers,
  AdminGetUserData,
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffData,
  AdminStudentInfoCreate,
  AdminStudentInfoUpdate,
  BaseStudentInfo,
} from "~/api/admin/admin.dto";

import { AdminApi } from "~/api/admin/admin.api";
import { AdminService } from "~/services/adminService";

const getAdminService = () => {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is not initialized");
  return new AdminService(new AdminApi($api));
};

// --- User service ---
export const serviceFormUser: UseFormService<
  AdminCreateUser, // create
  AdminUpdateUsers, // update
  never, // replace
  AdminGetUserData // get
> = {
  create: (data) => getAdminService().createUser(data),
  update: (id, data) => getAdminService().updateUser(id, data), // now OK
};
// --- Staff service ---
export const serviceFormStaff: UseFormService<
  AdminCreateStaff,
  AdminUpdateStaff,
  never,
  AdminGetStaffData
> = {
  create: (data) => getAdminService().createStaff(data),
  update: (id, data) => getAdminService().updateStaff(id, data),
  getDetail: (id) => getAdminService().getStaffDetail(id),
};

export const serviceFormStudent: UseFormService<
  never,
  never,
  AdminStudentInfoUpdate,
  BaseStudentInfo
> = {
  replace: (id, data) => getAdminService().updateStudentInfo(id, data),
  getDetail: (id) => getAdminService().getStudentInfo(id),
};
