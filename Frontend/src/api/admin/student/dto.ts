import type { ApiResponse } from "~/api/types/common/api-response.type";
import type { StudentInfoBaseDataDTO } from "~/api/types/student.dto";

export type AdminCreateStudentInfo = StudentInfoBaseDataDTO["student_info"];
export type AdminUpdateStudentInfo = Partial<
  StudentInfoBaseDataDTO["student_info"]
>;
export type AdminStudentInfoResponse = ApiResponse<StudentInfoBaseDataDTO>;
