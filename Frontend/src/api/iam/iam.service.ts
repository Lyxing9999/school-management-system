import { useMessage } from "~/composables/common/useMessage";
import { useRouter } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";
import { AuthApi } from "~/api/iam/iam.api";
import { Role } from "~/api/types/enums/role.enum";
import type { UserRegisterForm, UserLoginForm } from "~/api/iam/iam.dto";
import { isAxiosError } from "axios";

export class AuthService {
  private router = useRouter();
  private authStore = useAuthStore();
  private message = useMessage();

  constructor(private authApi: AuthApi) {}

  private validateCredentials(form: UserRegisterForm | UserLoginForm): boolean {
    if (!form.email || !form.password) {
      this.message.showWarning("Please fill in all fields");
      return false;
    }
    return true;
  }

  async login(form: UserLoginForm): Promise<void | null> {
    if (!this.validateCredentials(form)) return null;

    try {
      const data = await this.authApi.login(form);

      const token = data?.access_token;
      const user = data?.user;

      if (!token || !user) {
        this.message.showError("Invalid response from server");
        return null;
      }

      this.authStore.setToken(token);
      this.authStore.setUser(user);

      this.message.showSuccess("Logged in successfully");
      await this.redirectByRole(user.role);
      return;
    } catch (err) {
      if (isAxiosError(err)) {
        const msg =
          (err.response?.data as any)?.msg ||
          (err.response?.data as any)?.message ||
          err.message ||
          "Login failed";
        this.message.showError(String(msg));
        return null;
      }

      this.message.showError("Login failed");
      return null;
    }
  }

  async logout(): Promise<void> {
    try {
      await this.authApi.logout();
    } catch {
      // ignore
    } finally {
      this.authStore.clear();
      await this.router.push("/auth/login");
      this.message.showSuccess("Logged out successfully");
    }
  }

  private async redirectByRole(role: Role) {
    switch (role) {
      case Role.ADMIN:
        await this.router.push("/admin/dashboard");
        return;
      case Role.TEACHER:
        await this.router.push("/teacher/dashboard");
        return;
      case Role.STUDENT:
        await this.router.push("/student/dashboard");
        return;
      default:
        this.authStore.clear();
        this.message.showError("Unknown role. Please login again.");
        await this.router.push("/auth/login");
        return;
    }
  }
}
