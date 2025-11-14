import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AdminCreateSubject,
  AdminUpdateSubject,
  AdminGetSubjectsData,
} from "./dto";
import { SubjectApi } from "../subject/api";

export class SubjectService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private subjectApi: SubjectApi) {}

  async getSubjects() {
    const { data } = await this.safeApiCall<AdminGetSubjectsData>(() =>
      this.subjectApi.getSubjects()
    );
    return data!;
  }

  async getSubjectById(id: string) {
    const { data } = await this.safeApiCall<AdminGetSubjectsData>(() =>
      this.subjectApi.getSubjectById(id)
    );
    return data!;
  }

  async createSubject(subjectData: AdminCreateSubject) {
    const { data } = await this.safeApiCall<AdminGetSubjectsData>(() =>
      this.subjectApi.createSubject(subjectData)
    );
    return data!;
  }

  async updateSubject(id: string, subjectData: AdminUpdateSubject) {
    const { data } = await this.safeApiCall<AdminGetSubjectsData>(() =>
      this.subjectApi.updateSubject(id, subjectData)
    );
    return data!;
  }

  async deleteSubject(id: string) {
    const { data } = await this.safeApiCall<AdminGetSubjectsData>(() =>
      this.subjectApi.deleteSubject(id)
    );
    return data!;
  }
}
