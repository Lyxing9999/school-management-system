import { AdminApi } from "~/api/admin/admin.api";
import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminGetUserData,
  AdminGetPageUserData,
  AdminCreateUser,
  AdminUpdateUsers,
  AdminCreateClass,
  AdminGetClass,
  AdminFindTeacherSelect,
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffData,
  BaseStudentInfo,
  AdminStudentInfoUpdate,
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
  ): Promise<AdminGetPageUserData> {
    const { data } = await this.safeApiCall<AdminGetPageUserData>(
      this.adminApi.getUsers(roles, page, pageSize),
      {
        showSuccessNotification: options.showSuccessNotification ?? false,
        showErrorNotification: options.showErrorNotification ?? true,
      }
    );
    return data!;
  }

  async createUser(userData: AdminCreateUser): Promise<AdminGetUserData> {
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
    userData: AdminUpdateUsers
  ): Promise<AdminGetUserData> {
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
    const { data } = await this.safeApiCall<AdminGetStaffData>(
      this.adminApi.createStaff(staffData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async updateStaff(id: string, staffData: AdminUpdateStaff) {
    const { data } = await this.safeApiCall<AdminGetStaffData>(
      this.adminApi.updateStaff(id, staffData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async getStaffDetail(id: string) {
    console.log(this.adminApi.getStaffDetail(id));
    const { data } = await this.safeApiCall<AdminGetStaffData>(
      this.adminApi.getStaffDetail(id),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async getStudentInfo(id: string) {
    const { data } = await this.safeApiCall<BaseStudentInfo>(
      this.adminApi.getStudentInfo(id),
      {
        showSuccessNotification: false,
        showErrorNotification: true,
      }
    );
    return data!;
  }
  async updateStudentInfo(id: string, studentData: AdminStudentInfoUpdate) {
    const { data } = await this.safeApiCall<BaseStudentInfo>(
      this.adminApi.updateStudentInfo(id, studentData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }
}
