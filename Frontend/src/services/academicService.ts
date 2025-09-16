import { AcademicApi } from "~/api/academic/academic.api";
import { useApiUtils } from "~/utils/useApiUtils";
import type { AcademicFindClassDTOList } from "~/api/academic/academic.dto";

export class AcademicService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private academicApi: AcademicApi) {}
  // safeApiCall automatically unwraps the backend response and returns only the `data` field
  async getClasses(): Promise<AcademicFindClassDTOList | null> {
    const res = await this.safeApiCall<AcademicFindClassDTOList>(
      this.academicApi.getClasses(),
      {
        showSuccessNotification: false,
      }
    );
    if (!res) return null;
    return res;
  }
}
