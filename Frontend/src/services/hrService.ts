import { useApiUtils } from "~/utils/useApiUtils";
import { HrApi } from "~/api/hr/hr.api";
export class HrService {
  constructor(private hrApi: HrApi) {}

  private safeApiCall = useApiUtils().safeApiCall;

  async getEmployees(
    page: number,
    pageSize: number,
    options: {
      showSuccessNotification?: boolean;
      showErrorNotification?: boolean;
    } = {}
  ) {
    const res = await this.safeApiCall<any>(
      this.hrApi.getEmployees(page, pageSize)
    );

    if (!res) return null;

    return res;
  }

  async getDetail(id: string) {
    const res = await this.safeApiCall<any>(this.hrApi.getEmployeeDetail(id));
    if (!res) return null;
    return res;
  }

  async createEmployee(employeeData: any) {
    const res = await this.safeApiCall<any>(
      this.hrApi.createEmployee(employeeData),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    if (!res) return null;
    return res;
  }
}
