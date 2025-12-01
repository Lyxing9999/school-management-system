// ~/api/user/service.ts
import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
import type {
  AdminCreateUser,
  AdminUpdateUser,
  AdminGetUserData,
  AdminGetPageUserData,
  AdminStudentListNameSelectDTO,
} from "./dto";
import { UserApi } from "../user/api";
import { Role } from "~/api/types/enums/role.enum";

export class UserService {
  private callApi = useApiUtils().callApi;

  constructor(private userApi: UserApi) {}

  async getUserPage(
    roles: Role | Role[],
    page: number,
    pageSize: number,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminGetPageUserData>(
      () => this.userApi.getUserPage(roles, page, pageSize),
      { showSuccess: false, ...(options ?? {}) }
    );
    return data!;
  }

  async listStudentNamesSelect(options?: ApiCallOptions) {
    const data = await this.callApi<AdminStudentListNameSelectDTO>(
      () => this.userApi.listStudentNamesSelect(),
      options
    );
    return data!;
  }

  async createUser(userData: AdminCreateUser, options?: ApiCallOptions) {
    const data = await this.callApi<AdminGetUserData>(
      () => this.userApi.createUser(userData),
      options
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
      options
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
}
