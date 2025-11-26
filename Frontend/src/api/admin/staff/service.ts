import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminCreateStaff,
  AdminUpdateStaff,
  AdminGetStaffData,
  AdminTeacherSelectListData,
  AdminStaffNameSelectData,
} from "./dto";
import { StaffApi } from "../staff/api";

export class StaffService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private staffApi: StaffApi) {}

  async getTeacherSelect() {
    const { data } = await this.safeApiCall<AdminTeacherSelectListData>(() =>
      this.staffApi.getTeacherSelect()
    );

    return data!;
  }
  async getStaffNameSelect() {
    const { data } = await this.safeApiCall<AdminStaffNameSelectData>(() =>
      this.staffApi.getStaffNameSelect()
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
