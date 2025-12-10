// ~/api/staff/service.ts
import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
import type {
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffData,
  AdminTeacherSelectListData,
  AdminStaffNameSelectData,
} from "./staff.dto";
import { StaffApi } from "./staff.api";

export class StaffService {
  private callApi = useApiUtils().callApi;

  constructor(private staffApi: StaffApi) {}

  // Queries
  async listTeacherSelect(options?: ApiCallOptions) {
    const data = await this.callApi<AdminTeacherSelectListData>(
      () => this.staffApi.listTeacherSelect(),
      options
    );
    return data!;
  }

  async listStaffNameSelect(options?: ApiCallOptions) {
    const data = await this.callApi<AdminStaffNameSelectData>(
      () => this.staffApi.listStaffNameSelect(),
      options
    );
    return data!;
  }

  async getStaffDetail(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminGetStaffData>(
      () => this.staffApi.getStaffDetail(id),
      options
    );
    return data!;
  }

  // Commands
  async createStaff(staffData: AdminCreateStaff, options?: ApiCallOptions) {
    const data = await this.callApi<AdminGetStaffData>(
      () => this.staffApi.createStaff(staffData),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data!;
  }

  async updateStaff(
    id: string,
    staffData: AdminUpdateStaff,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminGetStaffData>(
      () => this.staffApi.updateStaff(id, staffData),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data!;
  }
}
