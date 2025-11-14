import type { UseFormService } from "~/services/types";
import type {
  AcademicStudentInfoUpdate,
  AcademicUpdateStudentData,
  AcademicGetStudentResponse,
  AcademicGetStudentsPageData,
  AcademicGetStudentPageResponse,
  AcademicCreateStudentData,
  AcademicStudentInfoResponse,
  AcademicStudentData,
} from "~/api/academic/academic.dto";
import type { BaseStudentInfo } from "~/api/types/student.dto";
import { AcademicService } from "~/services/academicService";
import { AcademicApi } from "~/api/academic/academic.api";

const getAcademicService = () => {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is not initialized");
  return new AcademicService(new AcademicApi($api));
};
import type { AdminListFilter } from "~/services/formServices/adminFormService";

export const serviceFormStudentIAM: UseFormService<
  AcademicCreateStudentData,
  AcademicUpdateStudentData,
  any,
  AcademicStudentData,
  AcademicStudentData,
  AdminListFilter
> = {
  create: (data) => getAcademicService().createStudent(data),
  update: (id, data) => getAcademicService().updateStudent(id, data),
  delete: (id) => getAcademicService().deleteStudent(id),
  page: async (filter?: AdminListFilter) => {
    const page = filter?.page ?? 1;
    const pageSize = filter?.pageSize ?? 10;

    const res = await getAcademicService().getStudentsPage(page, pageSize);
    return { items: res.users, total: res.total };
  },
};

export const serviceFormStudentInfo: UseFormService<
  any,
  AcademicStudentInfoUpdate,
  any,
  BaseStudentInfo,
  AcademicStudentInfoResponse,
  any
> = {
  update: (user_id, data) =>
    getAcademicService().createOrUpdateStudentInfo(user_id, data),
  delete: (user_id) => getAcademicService().deleteStudent(user_id),
  getDetail: (id: string): Promise<BaseStudentInfo> =>
    getAcademicService().getStudentInfo(id),
};
