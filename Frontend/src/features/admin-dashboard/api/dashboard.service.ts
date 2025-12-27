import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
import { DashboardApi } from "./dashboard.api";
import type {
  AdminDashboardDTO,
  AdminDashboardFilterDTO,
} from "../api/dashboard.dto";

export class DashboardService {
  private callApi = useApiUtils().callApi;

  constructor(private dashboardApi: DashboardApi) {}

  /**
   * Get admin dashboard data with optional filters.
   *
   * @param filters { date_from?: string; date_to?: string; term?: string }
   * @param options ApiCallOptions (showError, loadingRef, etc.)
   */
  async getDashboardData(
    filters?: AdminDashboardFilterDTO,
    options?: ApiCallOptions
  ): Promise<AdminDashboardDTO> {
    const data = await this.callApi<AdminDashboardDTO>(
      () => this.dashboardApi.getDashboardData(filters),
      options
    );

    // callApi returns T | null typically, so enforce here
    if (!data) throw new Error("Dashboard service returned null.");

    return data;
  }
}
