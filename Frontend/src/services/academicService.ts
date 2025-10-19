import { AcademicApi } from "~/api/academic/academic.api";
import { useApiUtils } from "~/utils/useApiUtils";
import type {
  AcademicGetStudentsPageData,
  AcademicGetClassData,
  AcademicGetTeacherSelect,
  AcademicStudentInfoUpdate,
  AcademicUpdateStudentData,
  AcademicCreateStudentData,
  AcademicStudentData,
  AcademicStudentInfoData,
  AcademicCreateClassData,
} from "~/api/academic/academic.dto";
import type { BaseStudentInfo } from "~/api/types/baseStudentInfo";
export class AcademicService {
  private safeApiCall = useApiUtils().safeApiCall;
  constructor(private academicApi: AcademicApi) {}
  // safeApiCall automatically unwraps the backend response and returns only the `data` field
  async getStudentsPage(
    page: number,
    pageSize: number
  ): Promise<AcademicGetStudentsPageData> {
    const { data } = await this.safeApiCall<AcademicGetStudentsPageData>(
      this.academicApi.getStudentsPage(page, pageSize),
      {
        showSuccessNotification: false,
      }
    );
    console.log("Page:", page, "PageSize:", pageSize);
    return data!;
  }
  async createStudent(payload: AcademicCreateStudentData) {
    const { data } = await this.safeApiCall<AcademicStudentData>(
      this.academicApi.createStudent(payload),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    return data!;
  }

  async updateStudent(user_id: string, payload: AcademicUpdateStudentData) {
    const { data } = await this.safeApiCall<AcademicUpdateStudentData>(
      this.academicApi.updateStudent(user_id, payload),
      {
        showSuccessNotification: true,
      }
    );
    return data!;
  }

  async deleteStudent(user_id: string) {
    const { data } = await this.safeApiCall<AcademicUpdateStudentData>(
      this.academicApi.deleteStudent(user_id),
      {
        showSuccessNotification: true,
      }
    );
    return data!;
  }
  async getStudentInfo(user_id: string) {
    const { data } = await this.safeApiCall<BaseStudentInfo>(
      this.academicApi.getStudentInfo(user_id),
      {
        showSuccessNotification: false,
      }
    );
    return data!;
  }
  async createOrUpdateStudentInfo(
    user_id: string,
    payload: AcademicStudentInfoUpdate
  ) {
    const { data } = await this.safeApiCall<AcademicStudentInfoData>(
      this.academicApi.updateStudentInfo(user_id, payload),
      { showSuccessNotification: true }
    );
    return data!;
  }
  // --- Teacher select ---
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

  // --- Class service ---
  async getClasses(): Promise<AcademicGetClassData[]> {
    const { data } = await this.safeApiCall<AcademicGetClassData[]>(
      this.academicApi.getClasses(),
      {
        showSuccessNotification: false,
      }
    );
    return data!;
  }
}
