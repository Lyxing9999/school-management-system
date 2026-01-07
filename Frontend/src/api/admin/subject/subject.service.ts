// ~/api/subject/service.ts
import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";
import type {
  AdminSubjectDataDTO,
  AdminCreateSubject,
  AdminSubjectPaginatedDTO,
  AdminSubjectNameSelectDTO,
} from "./subject.dto";
import { SubjectApi } from "./subject.api";

export class SubjectService {
  private callApi = useApiUtils().callApi;

  constructor(private subjectApi: SubjectApi) {}

  // ============
  // QUERY
  // ============

  async getSubjects(
    params?: {
      status?: "all" | "active" | "inactive";
      page?: number;
      page_size?: number;
      search?: string | null;
    },
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminSubjectPaginatedDTO>(
      () => this.subjectApi.getSubjects(params),
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

  async updateSubject(
    id: string,
    subjectData: Partial<AdminCreateSubject>,
    options?: ApiCallOptions
  ) {
    const data = await this.callApi<AdminSubjectDataDTO>(
      () => this.subjectApi.updateSubject(id, subjectData),
      { showSuccess: true, ...(options ?? {}) }
    );
    return data!;
  }
  async softDeleteSubject(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<AdminSubjectDataDTO>(
      () => this.subjectApi.softDeleteSubject(id),
      { showSuccess: true, ...(options ?? {}) }
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
  async listSubjectNameSelect() {
    const data = await this.callApi<AdminSubjectNameSelectDTO>(
      () => this.subjectApi.listSubjectNameSelect(),
      { showSuccess: false }
    );
    return data!;
  }
}
