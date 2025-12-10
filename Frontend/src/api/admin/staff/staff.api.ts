import type { AxiosInstance } from "axios";
import type {
  AdminCreateStaff,
  AdminGetStaffResponse,
  AdminUpdateStaff,
  AdminGetStaffSelectResponse,
  AdminTeacherSelectListResponse,
} from "./staff.dto";

export class StaffApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/staff"
  ) {}

  async listStaffNameSelect(): Promise<AdminGetStaffSelectResponse> {
    const res = await this.$api.get<AdminGetStaffSelectResponse>(
      `${this.baseURL}/name-select`
    );
    return res.data;
  }

  async listTeacherSelect(): Promise<AdminTeacherSelectListResponse> {
    const res = await this.$api.get<AdminTeacherSelectListResponse>(
      `${this.baseURL}/teacher-select`
    );
    return res.data;
  }

  async createStaff(
    staffData: AdminCreateStaff
  ): Promise<AdminGetStaffResponse> {
    const res = await this.$api.post<AdminGetStaffResponse>(
      this.baseURL,
      staffData
    );
    return res.data;
  }

  async updateStaff(
    id: string,
    staffData: AdminUpdateStaff
  ): Promise<AdminGetStaffResponse> {
    const res = await this.$api.patch<AdminGetStaffResponse>(
      `${this.baseURL}/${id}`,
      staffData
    );
    return res.data;
  }

  async deleteStaff(id: string): Promise<AdminGetStaffResponse> {
    const res = await this.$api.delete<AdminGetStaffResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }

  async getStaffDetail(id: string): Promise<AdminGetStaffResponse> {
    const res = await this.$api.get<AdminGetStaffResponse>(
      `${this.baseURL}/${id}`
    );
    return res.data;
  }
}
