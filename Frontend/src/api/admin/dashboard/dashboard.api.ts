// ~/api/admin/dashboard/dashboard.api.ts
import type { AxiosInstance } from "axios";
import type {
  AdminDashboardResponse,
  AdminDashboardFilterDTO,
} from "~/api/admin/dashboard/dashboard.dto";

export class DashboardApi {
  constructor(
    private $api: AxiosInstance,
    private baseURL = "/api/admin/dashboard"
  ) {}

  async getDashboardData(filters?: AdminDashboardFilterDTO) {
    const res = await this.$api.get<AdminDashboardResponse>(this.baseURL, {
      params: filters, // will send ?date_from=&date_to=&term=
    });
    return res.data;
  }
}
