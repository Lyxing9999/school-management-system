import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminCreateUser,
  AdminUpdateUser,
  AdminGetUserData,
  AdminGetPageUserData,
} from "./dto";
import { UserApi } from "../user/api";
import { Role } from "~/api/types/enums/role.enum";

export class UserService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private userApi: UserApi) {}

  async getUserPage(roles: Role | Role[], page: number, pageSize: number) {
    const { data } = await this.safeApiCall<AdminGetPageUserData>(
      () => this.userApi.getUserPage(roles, page, pageSize),
      {
        showSuccessNotification: false,
      }
    );
    return data!;
  }

  async createUser(userData: AdminCreateUser) {
    const { data } = await this.safeApiCall<AdminGetUserData>(() =>
      this.userApi.createUser(userData)
    );
    return data!;
  }

  async updateUser(id: string, userData: AdminUpdateUser) {
    const { data } = await this.safeApiCall<AdminGetUserData>(() =>
      this.userApi.updateUser(id, userData)
    );
    return data!;
  }

  async deleteUser(id: string) {
    const { data } = await this.safeApiCall(() => this.userApi.deleteUser(id), {
      showSuccessNotification: true,
      showErrorNotification: true,
    });
    return data!;
  }
}
