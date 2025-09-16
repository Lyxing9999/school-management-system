import type { AxiosInstance } from "axios";
import type { AcademicFindClassResponseDTOList } from "~/api/academic/academic.dto";

export class AcademicApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/academic") {}
  async getClasses(): Promise<AcademicFindClassResponseDTOList> {
    const response = await this.$api.get<AcademicFindClassResponseDTOList>(
      `${this.baseURL}/classes`
    );
    return response.data;
  }
}
