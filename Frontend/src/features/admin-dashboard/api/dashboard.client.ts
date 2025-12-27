import { DashboardApi } from "./dashboard.api";
import { DashboardService } from "./dashboard.service";
export function createDashboardService() {
  const { $api } = useNuxtApp();
  const api = new DashboardApi($api);
  return new DashboardService(api);
}
