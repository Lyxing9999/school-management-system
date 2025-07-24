import type { AxiosInstance } from "axios";
import type { User } from "~/types/models/User";
import type { Role } from "~/types/models/User";
import type { RoleDataMap, UserDetail } from "~/types/userServiceInterface";
import { UserStoreError } from "~/errors/UserStoreError";
import type { UserDetailResponse } from "~/types/userServiceInterface";

export class UserService {
  private baseURL = "/api/admin/";
  constructor(private $api: AxiosInstance) {}

  async listUsers(): Promise<User[]> {
    const res = await this.$api.get<{ data: User[] }>(this.baseURL);
    if (res.data.data.length === 0) {
      throw new UserStoreError("No users found", "NO_USERS_FOUND", null);
    }

    return res.data.data;
  }

  async getUserDetails<T extends keyof RoleDataMap = keyof RoleDataMap>(
    id: string
  ): Promise<UserDetailResponse<T>> {
    const res = await this.$api.get<{ data: UserDetailResponse<T> }>(
      `${this.baseURL}users/detail/${id}`
    );

    if (!res.data.data) {
      throw new UserStoreError(
        `No user details found for id ${id}`,
        "USER_NOT_FOUND",
        res.data.data
      );
    }

    return res.data.data;
  }

  async createUser(userData: any) {
    const res = await this.$api.post(`${this.baseURL}users`, userData);
    if (res.status !== 201 || !res.data.success) {
      throw new UserStoreError(
        res.data.message || "Failed to create user",
        "CREATE_USER_FAILED",
        res.data.data
      );
    }
    return res;
  }
  async updateUser(id: string, userData: any) {
    try {
      const res = await this.$api.patch(`${this.baseURL}users/${id}`, userData);
      return res.data.data;
    } catch (error: any) {
      console.error("Server error:", error.response?.data);

      throw error;
    }
  }
  async deleteUser(id: string) {
    try {
      const res = await this.$api.delete(`${this.baseURL}users/${id}`);
      if (res.status === 200) {
        return res.data.data;
      } else {
        throw new UserStoreError(
          "Failed to delete user",
          "DELETE_USER_FAILED",
          res.data
        );
      }
    } catch (error) {
      throw new UserStoreError(
        "Failed to delete user",
        "DELETE_USER_FAILED",
        error
      );
    }
  }

  async countByRole(): Promise<Record<Role, number>> {
    const res = await this.$api.get<{ data: Record<string, number> }>(
      `${this.baseURL}users/count-by-role`
    );
    return res.data.data as Record<Role, number>;
  }

  async compareGrowthStatsByRole(
    dates: Record<string, string | number>
  ): Promise<Record<string, number>> {
    const res = await this.$api.get<{ data: Record<string, number> }>(
      `${this.baseURL}users/growth-stats-by-role`,
      {
        params: dates,
      }
    );
    if (!res.data.data) {
      throw new UserStoreError(
        `Failed to compare growth stats by role`,
        "COMPARE_GROWTH_STATS_BY_ROLE_FAILED",
        res.data
      );
    }
    return res.data.data;
  }
  async editUserDetail(user_id: string, userData: Partial<UserDetail>) {
    const res = await this.$api.patch(
      `${this.baseURL}users/edit-user-detail/${user_id}`,
      userData
    );
    if (!res.data.data) {
      throw new UserStoreError(
        `Failed to edit user detail`,
        "EDIT_USER_DETAIL_FAILED",
        res.data
      );
    }
    return res.data.data;
  }
}
