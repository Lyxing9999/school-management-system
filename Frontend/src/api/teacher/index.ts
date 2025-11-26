//api
import { TeacherApi } from "./api";
//service
import { TeacherService } from "./service";

/**
 * Lazy singleton pattern
 */
let _teacherService: ReturnType<typeof createTeacherService> | null = null;

function createTeacherService() {
  const { $api } = useNuxtApp();
  if (!$api) throw new Error("$api is undefined.");

  const teacherApi = {
    teacher: new TeacherApi($api),
  };

  return {
    teacher: new TeacherService(teacherApi.teacher),
  };
}

export const teacherService = () =>
  (_teacherService ??= createTeacherService());
