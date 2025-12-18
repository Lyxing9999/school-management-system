import type { AxiosInstance } from "axios";
import type {
  AdminGetPageUserResponse,
  AdminCreateUser,
  AdminGetUserResponse,
  AdminUpdateUser,
  AdminUpdateUserStatus,
} from "./user.dto";

import { Role } from "~/api/types/enums/role.enum";
import { Status } from "~/api/types/enums/status.enum";
export class UserApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/users"
  ) {}

  async getUserPage(
    roles: Role | Role[],
    page: number,
    pageSize: number,
    q?: string,
    signal?: AbortSignal
  ): Promise<AdminGetPageUserResponse> {
    const params: Record<string, any> = { page, page_size: pageSize };

    if (Array.isArray(roles)) params["role[]"] = roles;
    else params.role = roles;

    const search = String(q ?? "").trim();
    if (search) params.search = search;

    const res = await this.$api.get<AdminGetPageUserResponse>(this.baseURL, {
      params,
      signal,
    });

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

  async setUserStatus(id: string, status: Status) {
    const res = await this.$api.patch<AdminGetUserResponse>(
      `${this.baseURL}/${id}/status`,
      { status }
    );
    return res.data;
  }
}
