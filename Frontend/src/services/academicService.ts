import { AcademicApi } from "~/api/academic/academic.api";
import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AcademicGetStudentsPayload,
  AcademicCreateClassPayload,
  AcademicBaseClassDataDTO,
  AcademicGetTeacherSelect,
} from "~/api/academic/academic.dto";

export class AcademicService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private academicApi: AcademicApi) {}
  // safeApiCall automatically unwraps the backend response and returns only the `data` field
  async getStudents(
    page: number,
    pageSize: number
  ): Promise<AcademicGetStudentsPayload | null> {
    const { data } = await this.safeApiCall<AcademicGetStudentsPayload>(
      this.academicApi.getStudents(page, pageSize),
      {
        showSuccessNotification: false,
      }
    );
    if (!data) return null;
    return data!;
  }

  async getClasses(): Promise<AcademicBaseClassDataDTO[] | null> {
    const { data } = await this.safeApiCall<AcademicBaseClassDataDTO[]>(
      this.academicApi.getClasses(),
      {
        showSuccessNotification: false,
      }
    );
    if (!data) return null;
    return data!;
  }

  async createClass(
    payload: AcademicCreateClassPayload
  ): Promise<AcademicBaseClassDataDTO> {
    const { data } = await this.safeApiCall<AcademicBaseClassDataDTO>(
      this.academicApi.createClass(payload),
      {
        showSuccessNotification: true,
      }
    );
    return data!;
  }

  async getTeacherForSelect(
    searchText: string
  ): Promise<AcademicGetTeacherSelect[] | null> {
    const { data } = await this.safeApiCall<AcademicGetTeacherSelect[] | null>(
      this.academicApi.getTeacherForSelect(searchText),
      {
        showSuccessNotification: false,
      }
    );
    if (!data) return null;
    return data!;
  }
  async getTeacherNames(): Promise<AcademicGetTeacherSelect[] | null> {
    const { data } = await this.safeApiCall<AcademicGetTeacherSelect[] | null>(
      this.academicApi.getTeacherNames(),
      {
        showSuccessNotification: false,
      }
    );
    if (!data) return null;
    return data!;
  }
}
