// ~/api/subject/service.ts
import { useApiUtils, type ApiCallOptions } from "~/utils/useApiUtils";
import type {
  AdminSubjectListDTO,
  AdminSubjectDataDTO,
  AdminCreateSubject,
} from "./subject.dto";
import { SubjectApi } from "./subject.api";

export class SubjectService {
  private callApi = useApiUtils().callApi;

  constructor(private subjectApi: SubjectApi) {}

  // ============
  // QUERY
  // ============

  async getSubjects(options?: ApiCallOptions) {
    const data = await this.callApi<AdminSubjectListDTO>(
      () => this.subjectApi.getSubjects(),
      options
    );
    return data!;
  }

  async getSubject(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminSubjectDataDTO>(
      () => this.subjectApi.getSubject(id),
      options
    );
    return data!;
  }

  // ============
  // COMMANDS
  // ============

  async createSubject(
    subjectData: AdminCreateSubject,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminSubjectDataDTO>(
      () => this.subjectApi.createSubject(subjectData),
      options
    );
    return data!;
  }

  async activateSubject(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminSubjectDataDTO>(
      () => this.subjectApi.activateSubject(id),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data!;
  }

  async deactivateSubject(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminSubjectDataDTO>(
      () => this.subjectApi.deactivateSubject(id),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data!;
  }
}
