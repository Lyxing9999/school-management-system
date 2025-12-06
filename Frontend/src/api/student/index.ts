//api
import { StudentApi } from "./student.api";
//service
import { StudentService } from "./student.service";

/**
 * Lazy singleton pattern
 */
let _studentService: ReturnType<typeof createStudentService> | null = null;

function createStudentService() {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is undefined.");

  const studentApi = {
    student: new StudentApi($api),
  };

  return {
    student: new StudentService(studentApi.student),
  };
}

export const studentService = () =>
  (_studentService ??= createStudentService());
