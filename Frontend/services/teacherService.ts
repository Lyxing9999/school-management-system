import type { AxiosInstance } from "axios";

export class TeacherService {
  constructor(private $api: AxiosInstance) {}
  private baseURL = "/api/teacher";

  async fetchCurrentTeacher() {
    try {
      const res = await this.$api.get(`${this.baseURL}/me`);
      console.log("hello");
      console.log(res.data);
      return res.data.data;
    } catch (e) {
      console.error("Error fetching teacher profile", e);
      return null;
    }
  }

  async createTeacher(teacherData: Record<string, any>) {
    try {
      const res = await this.$api.post(`${this.baseURL}/`, teacherData);
      return res.data.data;
    } catch (e) {
      console.error("Error creating teacher", e);
      return null;
    }
  }

  async getTeacherClasses() {
    const res = await this.$api.get(`${this.baseURL}/classes`);
    return res.data.data;
  }
}

// import ElMessage from "element-plus/es/components/message/index.mjs";
// import { TeacherModel } from "~/models/teacherModel";
// import { useNuxtApp } from "#imports";
// import type { Teacher } from "~/models/teacherModel";

// export class TeacherService {
//   private $api = useNuxtApp().$api;
//   private baseURL = "/api/teacher/";
//   async getAll(): Promise<Teacher[]> {
//     try {
//       const res = await this.$api.get("/me/teacher");
//       return res.data.map((t: Teacher) => new TeacherModel(t));
//     } catch (err) {
//       ElMessage.error("Failed to fetch teachers");
//       return [];
//     }
//   }
