import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminSubjectListDTO,
  AdminSubjectDataDTO,
  AdminCreateSubjectDTO,
} from "./dto";
import { SubjectApi } from "../subject/api";

export class SubjectService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private subjectApi: SubjectApi) {}

  async getSubjects() {
    const { data } = await this.safeApiCall<AdminSubjectListDTO>(
      () => this.subjectApi.getSubjects(),
      {
        showSuccessNotification: false,
      }
    );
    return data!;
  }

  async getSubject(id: string) {
    const { data } = await this.safeApiCall<AdminSubjectDataDTO>(() =>
      this.subjectApi.getSubject(id)
    );
    return data!;
  }

  async createSubject(subjectData: AdminCreateSubjectDTO) {
    const { data } = await this.safeApiCall<AdminSubjectDataDTO>(
      () => this.subjectApi.createSubject(subjectData),
      {
        showSuccessNotification: true,
      }
    );
    return data!;
  }

  async activateSubject(id: string) {
    const { data } = await this.safeApiCall<AdminSubjectDataDTO>(() =>
      this.subjectApi.activateSubject(id)
    );
    return data!;
  }

  async deactivateSubject(id: string) {
    const { data } = await this.safeApiCall<AdminSubjectDataDTO>(() =>
      this.subjectApi.deactivateSubject(id)
    );
    return data!;
  }
}
