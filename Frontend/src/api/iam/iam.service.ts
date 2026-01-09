import { useMessage } from "~/composables/common/useMessage";
import { useRouter, useCookie } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";
import { AuthApi } from "~/api/iam/iam.api";
import { Role } from "~/api/types/enums/role.enum";
import type {
  UserRegisterForm,
  UserLoginForm,
  ResetPasswordConfirmForm,
  ChangePasswordForm,
  UpdateMePayload,
} from "~/api/iam/iam.dto";
import { isAxiosError } from "axios";

type AuthCookieUser = {
  id: string;
  username?: string;
  role: Role;
};

export class AuthService {
  private router = useRouter();
  private authStore = useAuthStore();
  private message = useMessage();

  // SSR-safe cookies (available on server + client)
  private tokenCookie = useCookie<string | null>("access_token", {
    sameSite: "lax",
    path: "/",
  });

  private roleCookie = useCookie<Role | null>("user_role", {
    sameSite: "lax",
    path: "/",
  });
  private studentHomeCookie = useCookie<"dashboard" | "attendance" | null>(
    "student_home",
    {
      sameSite: "lax",
      path: "/",
    }
  );
  /**
   * Optional (non-sensitive) cache so header can show name immediately
   * without waiting for /me (works on refresh).
   */
  private userCookie = useCookie<AuthCookieUser | null>("user_cache", {
    sameSite: "lax",
    path: "/",
  });

  constructor(private authApi: AuthApi) {}

  private validateCredentials(form: UserRegisterForm | UserLoginForm): boolean {
    if (!form.email || !form.password) {
      this.message.showWarning("Please fill in all fields");
      return false;
    }
    return true;
  }

  private persistAuth(token: string, user: any) {
    // Cookies
    this.tokenCookie.value = token;
    this.roleCookie.value = user.role;

    // Minimal cache for instant header
    this.userCookie.value = {
      id: String(user.id),
      username: user.username,
      role: user.role,
    };

    // Pinia
    this.authStore.setToken(token);
    this.authStore.setUser(user);
    this.authStore.setReady(true);
  }

  private clearAuth() {
    // Cookies
    this.tokenCookie.value = null;
    this.roleCookie.value = null;
    this.userCookie.value = null;

    // Pinia
    this.authStore.setToken("");
    this.authStore.setUser(null);
    this.authStore.setReady(true);
  }

  async login(form: UserLoginForm): Promise<void | null> {
    if (!this.validateCredentials(form)) return null;

    // while logging in, you may setReady(false) if you want
    this.authStore.setReady(false);

    try {
      const data = await this.authApi.login(form);

      const token = data?.access_token;
      const user = data?.user;

      if (!token || !user) {
        this.message.showError("Invalid response from server");
        this.authStore.setReady(true);
        return null;
      }

      this.persistAuth(token, user);

      this.message.showSuccess("Logged in successfully");
      await this.redirectByRole(user.role);
      return;
    } catch (err) {
      this.authStore.setReady(true);

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
      this.clearAuth();
      await navigateTo("/auth/login", { replace: true });
      this.message.showSuccess("Logged out successfully");
    }
  }

  async confirmResetPassword(form: ResetPasswordConfirmForm): Promise<boolean> {
    const token = String(form.token ?? "").trim();
    const newPassword = String(form.new_password ?? "");

    if (!token || !newPassword) {
      this.message.showWarning("Token and new password are required");
      return false;
    }

    try {
      const res = await this.authApi.confirmResetPassword({
        token,
        new_password: newPassword,
      });

      const msg =
        (res as any)?.data?.message ||
        (res as any)?.message ||
        "Password updated";
      this.message.showSuccess(String(msg));
      return true;
    } catch (err) {
      if (isAxiosError(err)) {
        const msg =
          (err.response?.data as any)?.msg ||
          (err.response?.data as any)?.message ||
          err.message ||
          "Reset password failed";
        this.message.showError(String(msg));
        return false;
      }

      this.message.showError("Reset password failed");
      return false;
    }
  }

  async changePassword(form: ChangePasswordForm): Promise<boolean> {
    const currentPassword = String(form.current_password ?? "");
    const newPassword = String(form.new_password ?? "");

    if (!currentPassword || !newPassword) {
      this.message.showWarning("Please fill in all fields");
      return false;
    }

    if (currentPassword === newPassword) {
      this.message.showWarning("New password must be different");
      return false;
    }

    try {
      const res = await this.authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      });

      const msg =
        (res as any)?.data?.message ||
        (res as any)?.message ||
        "Password changed";
      this.message.showSuccess(String(msg));

      await this.logout();
      return true;
    } catch (err) {
      if (isAxiosError(err)) {
        const msg =
          (err.response?.data as any)?.msg ||
          (err.response?.data as any)?.message ||
          err.message ||
          "Change password failed";
        this.message.showError(String(msg));
        return false;
      }

      this.message.showError("Change password failed");
      return false;
    }
  }

  async getMe() {
    return this.authApi.getMe();
  }
  async updateMe(payload: UpdateMePayload) {
    try {
      const data = await this.authApi.updateMe(payload);
      const user = (data as any)?.data ?? data;

      if (!user) {
        this.message.showError("Invalid response from server");
        return null;
      }

      // keep cookies + store in sync
      this.authStore.setUser(user);
      this.userCookie.value = {
        id: String(user.id),
        username: user.username,
        role: user.role,
      };

      this.message.showSuccess("Profile updated");
      return user;
    } catch (err) {
      if (isAxiosError(err)) {
        const msg =
          (err.response?.data as any)?.msg ||
          (err.response?.data as any)?.message ||
          err.message ||
          "Update failed";
        this.message.showError(String(msg));
        return null;
      }
      this.message.showError("Update failed");
      return null;
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

      case Role.STUDENT: {
        const home = this.studentHomeCookie.value || "dashboard";
        await this.router.push(
          home === "attendance" ? "/student/attendance" : "/student/dashboard"
        );
        return;
      }

      default:
        this.clearAuth();
        this.message.showError("Unknown role. Please login again.");
        await this.router.push("/auth/login");
        return;
    }
  }
}
