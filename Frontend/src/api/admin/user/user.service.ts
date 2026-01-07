import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";
import type {
  AdminCreateUser,
  AdminUpdateUser,
  AdminGetUserData,
  AdminGetPageUserData,
  AdminPasswordResetResponse,
} from "./user.dto";
import { UserApi } from "./user.api";
import { Role } from "~/api/types/enums/role.enum";
import { Status } from "~/api/types/enums/status.enum";
export class UserService {
  private callApi = useApiUtils().callApi;

  constructor(private userApi: UserApi) {}

  async getUserPage(
    roles: Role | Role[],
    page: number,
    pageSize: number,
    query?: string,
    signal?: AbortSignal,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminGetPageUserData>(
      () => this.userApi.getUserPage(roles, page, pageSize, query, signal),
      { showSuccess: false, ...(options ?? {}) }
    );
    return data!;
  }

  async createUser(userData: AdminCreateUser, options?: ApiCallOptions) {
    const data = await this.callApi<AdminGetUserData>(
      () => this.userApi.createUser(userData),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data!;
  }

  async updateUser(
    id: string,
    userData: AdminUpdateUser,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminGetUserData>(
      () => this.userApi.updateUser(id, userData),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data!;
  }

  async softDeleteUser(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<any>(
      () => this.userApi.softDeleteUser(id),
      { showSuccess: true, showError: true, ...(options ?? {}) }
    );
    return data!;
  }

  async hardDeleteUser(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<any>(
      () => this.userApi.hardDeleteUser(id),
      { showSuccess: true, showError: true, ...(options ?? {}) }
    );
    return data!;
  }

  async setUserStatus(id: string, status: Status) {
    const data = await this.callApi<AdminGetUserData>(
      () => this.userApi.setUserStatus(id, status),
      { showSuccess: true, showError: true }
    );
    return data!;
  }
  async requestPasswordReset(userId: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminPasswordResetResponse>(
      () => this.userApi.requestPasswordReset(userId),
      {
        showSuccess: false,
        showError: false,
        ...(options ?? {}),
      }
    );
    return data!;
  }
}
