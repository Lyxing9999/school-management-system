import type { AxiosInstance } from "axios";
import type {
  AdminDashboardFilterDTO,
  AdminDashboardResponse,
} from "./dashboard.dto.js";

export class DashboardApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/dashboard"
  ) {}

  async getDashboardData(filters?: AdminDashboardFilterDTO) {
    const res = await this.$api.get<AdminDashboardResponse>(this.baseURL, {
      params: filters,
    });

    return res.data;
  }
}
