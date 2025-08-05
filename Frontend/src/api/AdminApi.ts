import type { AxiosInstance } from "axios";
import type {
  AdminCreateUserResponseDTO,
  AdminUpdateUserResponseDTO,
  AdminUserDTO,
  AdminDeleteUserResponseDTO,
  AdminGetUserResponseDTO,
} from "~/types";

export class AdminApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/admin") {}

  async getUsers(): Promise<AdminGetUserResponseDTO> {
    const response = await this.$api.get<AdminGetUserResponseDTO>(
      `${this.baseURL}/users`
    );
    return response.data;
  }

  async createUser(
    user: AdminUserDTO.Create
  ): Promise<AdminCreateUserResponseDTO> {
    const response = await this.$api.post<AdminCreateUserResponseDTO>(
      `${this.baseURL}/users`,
      user
    );
    return response.data;
  }

  async updateUser(
    user: AdminUserDTO.Update
  ): Promise<AdminUpdateUserResponseDTO> {
    const response = await this.$api.put<AdminUpdateUserResponseDTO>(
      `${this.baseURL}/users/${user.id}`,
      user
    );
    return response.data;
  }

  async deleteUser(id: string): Promise<AdminDeleteUserResponseDTO> {
    const response = await this.$api.delete<AdminDeleteUserResponseDTO>(
      `${this.baseURL}/users/${id}`
    );
    return response.data;
  }
}
