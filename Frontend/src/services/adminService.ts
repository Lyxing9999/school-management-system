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
    const res = await this.safeApiCall<AdminGetPageUserData>(
      this.adminApi.getUsers(roles, page, pageSize),
      {
        showSuccessNotification: options.showSuccessNotification ?? false,
        showErrorNotification: options.showErrorNotification ?? true,
      }
    );

    return res;
  }

  async createUser(
    userData: AdminCreateUser
  ): Promise<AdminGetUserData | null> {
    const res = await this.safeApiCall<AdminGetUserData>(
      this.adminApi.createUser(userData),
      {
        showSuccessNotification: false,
      }
    );
    if (!res) return null;
    return res;
  }

  async updateUser(
    id: string,
    userData: AdminUpdateUser
  ): Promise<AdminGetUserData | null> {
    const res = await this.safeApiCall<AdminGetUserData>(
      this.adminApi.updateUser(id, userData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    if (!res) return null;
    return res;
  }

  async deleteUser(id: string) {
    return this.safeApiCall(this.adminApi.deleteUser(id), {
      showSuccessNotification: true,
      showErrorNotification: true,
    });
  }
  async createClass(classData: AdminCreateClass) {
    const res = await this.safeApiCall<AdminGetClass>(
      this.adminApi.createClass(classData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    if (!res) return null;
    return res;
  }
  async getTeacherSelect() {
    const res = await this.safeApiCall<AdminFindTeacherSelect[]>(
      this.adminApi.getTeacherSelect(),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    if (!res) return null;
    return res;
  }
}
