import type { AxiosInstance } from "axios";
import type {
  AdminGetPageUserResponse,
  AdminCreateUser,
  AdminGetUserResponse,
  AdminUpdateUser,
  AdminStudentListNameSelectResponse,
} from "./dto";
import { Role } from "~/api/types/enums/role.enum";

export class UserApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/users"
  ) {}

  async getUserPage(
    roles: Role | Role[],
    page: number,
    pageSize: number
  ): Promise<AdminGetPageUserResponse> {
    const params = { page, page_size: pageSize } as Record<string, any>;
    if (Array.isArray(roles)) params["role[]"] = roles;
    else params.role = roles;
    const res = await this.$api.get<AdminGetPageUserResponse>(this.baseURL, {
      params,
    });
    return res.data;
  }
  async getStudentNameSelect(): Promise<AdminStudentListNameSelectResponse> {
    const res = await this.$api.get<AdminStudentListNameSelectResponse>(
      `${this.baseURL}/student-select`
    );
    return res.data;
  }

  async createUser(userData: AdminCreateUser): Promise<AdminGetUserResponse> {
    const res = await this.$api.post<AdminGetUserResponse>(
      this.baseURL,
      userData
    );
    return res.data;
  }

  async updateUser(
    id: string,
    userData: AdminUpdateUser
  ): Promise<AdminGetUserResponse> {
    const res = await this.$api.patch<AdminGetUserResponse>(
      `${this.baseURL}/${id}`,
      userData
    );
    return res.data;
  }

  async softDeleteUser(id: string): Promise<AdminGetUserResponse> {
    const res = await this.$api.delete<AdminGetUserResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }

  async hardDeleteUser(id: string): Promise<AdminGetUserResponse> {
    const res = await this.$api.delete<AdminGetUserResponse>(
      `${this.baseURL}/${id}/hard`
    );
    return res.data;
  }
}
