import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffData,
  AdminGetStaffNameData,
} from "./dto";
import { StaffApi } from "../staff/api";

export class StaffService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private staffApi: StaffApi) {}

  async getStaffNameSelect(search: string, role: string) {
    const { data } = await this.safeApiCall<AdminGetStaffNameData>(() =>
      this.staffApi.getStaffNameSelect(search, role)
    );
    return data!;
  }

  async createStaff(staffData: AdminCreateStaff) {
    const { data } = await this.safeApiCall<AdminGetStaffData>(() =>
      this.staffApi.createStaff(staffData)
    );
    return data!;
  }

  async updateStaff(id: string, staffData: AdminUpdateStaff) {
    const { data } = await this.safeApiCall<AdminGetStaffData>(() =>
      this.staffApi.updateStaff(id, staffData)
    );
    return data!;
  }

  async getStaffDetail(id: string) {
    const { data } = await this.safeApiCall<AdminGetStaffData>(() =>
      this.staffApi.getStaffDetail(id)
    );
    return data!;
  }
}
