import { AdminApi } from "~/api/admin/admin.api";
import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminGetUserData,
  AdminGetPageUserData,
  AdminCreateUser,
  AdminUpdateUser,
  AdminCreateClass,
  AdminGetClass,
  AdminFindTeacherSelect,
  AdminCreateStaff,
  AdminUpdateStaff,
  adminGetstaffData,
} from "~/api/admin/admin.dto";
import { Role } from "~/api/types/enums/role.enum";
export class AdminService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private adminApi: AdminApi) {}

  async getUsers(
    roles: Role | Role[],
    page: number,
    pageSize: number,
    options: {
      showSuccessNotification?: boolean;
      showErrorNotification?: boolean;
    } = {}
  ): Promise<AdminGetPageUserData | null> {
    const { data } = await this.safeApiCall<AdminGetPageUserData>(
      this.adminApi.getUsers(roles, page, pageSize),
      {
        showSuccessNotification: options.showSuccessNotification ?? false,
        showErrorNotification: options.showErrorNotification ?? true,
      }
    );
    return data!;
  }

  async createUser(
    userData: AdminCreateUser
  ): Promise<AdminGetUserData | null> {
    const { data } = await this.safeApiCall<AdminGetUserData>(
      this.adminApi.createUser(userData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  } 

  async updateUser(
    id: string,
    userData: AdminUpdateUser
  ): Promise<AdminGetUserData | null> {
    const { data } = await this.safeApiCall<AdminGetUserData>(
      this.adminApi.updateUser(id, userData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async deleteUser(id: string) {
    const { data } = await this.safeApiCall(this.adminApi.deleteUser(id), {
      showSuccessNotification: true,
      showErrorNotification: true,
    });
    return data!;
  }
  async createClass(classData: AdminCreateClass) {
    const { data } = await this.safeApiCall<AdminGetClass>(
      this.adminApi.createClass(classData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async getTeacherSelect() {
    const { data } = await this.safeApiCall<AdminFindTeacherSelect[]>(
      this.adminApi.getTeacherSelect(),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async createStaff(staffData: AdminCreateStaff) {
    const { data } = await this.safeApiCall<adminGetstaffData>(
      this.adminApi.createStaff(staffData),
      {
        showSuccessNotification: false,
      }
    );
    return data!;
  }
  async updateStaff(id: string, staffData: AdminUpdateStaff) {
    const { data } = await this.safeApiCall<adminGetstaffData>(
      this.adminApi.updateStaff(id, staffData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
}
