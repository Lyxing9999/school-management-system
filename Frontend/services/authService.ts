import { useNuxtApp, useRuntimeConfig, useRouter } from "nuxt/app";
import { ElMessage } from "element-plus";
import type { AuthUser, LoginResponse } from "~/types/auth";
import { UserModel } from "~/models/userModel";
import { useAuthStore } from "~/stores/authStore";
import type { AxiosInstance } from "axios";
import type { User } from "~/types/models/User";
import { jwtDecode } from "jwt-decode";

export enum UserRole {
  Admin = "admin",
  Teacher = "teacher",
  Student = "student",
}
function isUserRole(role: string): role is UserRole {
  return Object.values(UserRole).includes(role as UserRole);
}

export class AuthService {
  private $api = useNuxtApp().$api as AxiosInstance;
  private router = useRouter();
  private config = useRuntimeConfig();
  private baseURL = "/api/auth/";
  async login(form: { username: string; password: string }) {
    if (!form.username || !form.password) {
      ElMessage.warning("Please fill in all fields");
      return;
    }

    try {
      const res = await this.$api.post<{ data: LoginResponse }>(
        `${this.baseURL}login`,
        form
      );
      if (!res?.data) {
        ElMessage.error("No data from server");
        return;
      }

      const token = res.data?.data?.access_token;
      if (!token) {
        ElMessage.error("Invalid response from server: no token");
        return;
      }

      // Decode the token to get user info directly
      const decodedRaw = jwtDecode(token) as {
        id: string;
        role: UserRole;
        username: string;
        email?: string;
      };
      if (!isUserRole(decodedRaw.role)) {
        ElMessage.error("Invalid role in token");
        return;
      }
      const decodedUser = {
        ...decodedRaw,
        role: decodedRaw.role,
      } as AuthUser;

      const authStore = useAuthStore();

      authStore.login(token, decodedUser);

      console.log("Logged in user from token:", decodedUser);

      this.redirectByRole(decodedUser.role);
    } catch (err) {
      console.error("Login failed", err);
      ElMessage.error("Login failed, please try again");
    }
  }

  loginWithGoogle() {
    window.location.href = `${this.config.public.apiBase}/auth/google/login`;
  }

  logout() {
    const authStore = useAuthStore();
    this.clearToken();
    authStore.logout();
    this.router.push("/auth/login");
    ElMessage.success("Logged out successfully");
  }
  getToken(): string | null {
    return localStorage.getItem("token");
  }

  private storeToken(token: string) {
    localStorage.setItem("token", token);
  }

  private clearToken() {
    localStorage.removeItem("token");
  }

  private redirectByRole(role: UserRole) {
    switch (role) {
      case UserRole.Admin:
        this.router.push("/admin/dashboard");
        break;
      case UserRole.Teacher:
        this.router.push("/teacher/dashboard");
        break;
      default:
        this.router.push("/student/dashboard");
    }
  }
}
