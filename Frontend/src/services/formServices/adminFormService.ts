// ~/services/formServices/adminFormService.ts
import type { UseFormService } from "~/services/types";
import type {
  AdminCreateUser,
  AdminUpdateUser,
  AdminGetUserData,
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffData,
  AdminStudentInfoUpdate,
  AdminGetPageUserData,
  AdminGetAllClassesResponse,
  AdminCreateSubject,
  AdminUpdateSubject,
  AdminSubjectResponse,
} from "~/api/admin/admin.dto";
import type { BaseStudentInfo } from "~/api/types/baseStudentInfo";
import { AdminApi } from "~/api/admin/admin.api";
import { AdminService } from "~/services/adminService";

const getAdminService = () => {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is not initialized");
  return new AdminService(new AdminApi($api));
};

import { Role } from "~/api/types/enums/role.enum";
import type { BaseSubject } from "~/api/types/baseSubject";
export interface AdminListFilter {
  page: number;
  pageSize: number;
  roles?: Role[];
  search?: string;
}

// --- User service ---
export const serviceFormUser: UseFormService<
  AdminCreateUser, // C - create
  AdminUpdateUser, // U - update
  any, // D - delete (not used)
  AdminGetUserData, // R - single user detail
  AdminGetUserData, // L - list item (same shape here)
  AdminListFilter // F - filter (with roles, page, pageSize)
> = {
  create: (data) => getAdminService().createUser(data),
  update: (id, data) => getAdminService().updateUser(id, data),
  delete: (id) => getAdminService().deleteUser(id),
  page: async (filter: AdminListFilter) => {
    const res = await getAdminService().getUsers(
      filter.roles || [],
      filter.page,
      filter.pageSize
    );

    const pageData: AdminGetPageUserData = {
      users: res.users,
      page: res.page,
      page_size: res.page_size,
      total: res.total,
      total_pages: res.total_pages,
    };

    return {
      items: pageData.users,
      total: pageData.total,
    };
  },
};
// --- Staff service ---
export const serviceFormStaff: UseFormService<
  AdminCreateStaff,
  AdminUpdateStaff,
  never,
  AdminGetStaffData,
  never
> = {
  create: (data) => getAdminService().createStaff(data),
  update: (id, data) => getAdminService().updateStaff(id, data),
  getDetail: (id) => getAdminService().getStaffDetail(id),
};

export const serviceFormStudent: UseFormService<
  any,
  AdminStudentInfoUpdate,
  any,
  BaseStudentInfo,
  any
> = {
  getDetail: (id) => getAdminService().getStudentInfo(id),
  update: (id, data: AdminStudentInfoUpdate | FormData) => {
    return getAdminService().updateStudentInfo(
      id,
      data as AdminStudentInfoUpdate
    );
  },
};

export const serviceClass: UseFormService<any, any, any, any, any> = {
  create: (data) => getAdminService().createClass(data),
  update: (id, data) => getAdminService().updateClass(id, data),
  getDetail: (id) => getAdminService().getClassById(id),
  all: async () => {
    const res = await getAdminService().getAllClasses();
    return Array.isArray(res) ? res : [res];
  },
};

export const serviceSubject: UseFormService<
  AdminCreateSubject,
  AdminUpdateSubject,
  any,
  any,
  any,
  BaseSubject
> = {
  create: (data) => getAdminService().createSubject(data),
  update: (id, data) => getAdminService().updateSubject(id, data),
  getDetail: (id) => getAdminService().getSubjectById(id),
  all: async () => {
    const res = await getAdminService().getSubjects();
    return Array.isArray(res) ? res : [res];
  },
};
