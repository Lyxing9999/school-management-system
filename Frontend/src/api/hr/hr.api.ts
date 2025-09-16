import type { AxiosInstance } from "axios";

export class HrApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/hr") {}

  async getEmployees(page: number, pageSize: number): Promise<any | null> {
    const res = await this.$api.get<any>(`${this.baseURL}/employees`, {
      params: {
        page,
        page_size: pageSize,
      },
    });
    if (!res) return null;
    return res.data;
  }

  async getEmployeeDetail(id: string): Promise<any | null> {
    const res = await this.$api.get<any>(
      `${this.baseURL}/employees/details/${id}`
    );
    if (!res) return null;
    return res.data;
  }
  async createEmployee(employeeData: any): Promise<any | null> {
    const res = await this.$api.post<any>(
      `${this.baseURL}/employees`,
      employeeData
    );
    if (!res) return null;
    return res.data;
  }
}
