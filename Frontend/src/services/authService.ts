import { ElMessage } from "element-plus";
import { jwtDecode } from "jwt-decode";
import { useRouter } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";
import { AuthApi } from "~/api/auth.api";
import { useApiUtils } from "~/utils/useApiUtils";
import { Role } from "~/types";
import type {
  UserRegisterForm,
  UserLoginForm,
  User,
  UserRegisterDataDTO,
  UserLoginDataDTO,
} from "~/types";

export class AuthService {
  private router = useRouter();
  private authStore = useAuthStore();
  private safeApiCall = useApiUtils().safeApiCall;

  constructor(private authApi: AuthApi) {}

  private validateCredentials(form: UserRegisterForm | UserLoginForm): boolean {
    if (!form.username || !form.password) {
      ElMessage.warning("Please fill in all fields");
      return false;
    }
    return true;
  }

  async register(form: UserRegisterForm): Promise<UserRegisterDataDTO | null> {
    if (!this.validateCredentials(form)) return null;

    const res = await this.safeApiCall<UserRegisterDataDTO>(
      this.authApi.registerUser(form)
    );
    if (!res) return null;
    await this.router.push("/auth/login");
    return res;
  }

  async login(form: UserLoginForm): Promise<void | null> {
    if (!this.validateCredentials(form)) return null;

    const response = await this.safeApiCall<UserLoginDataDTO>(
      this.authApi.login(form)
    );
    if (!response) return;

    const token = response.access_token;
    if (!token) {
      ElMessage.error("Invalid response from server: no token");
      return;
    }
    const decodedUser = jwtDecode(token) as User;
    this.authStore.login(token, decodedUser);

    await this.redirectByRole(decodedUser.role);
  }

  // loginWithGoogle() {
  //   this.authApi.loginWithGoogle(this.authApi);
  // }

  logout() {
    this.authStore.logout();
    this.router.push("/auth/login");
    ElMessage.success("Logged out successfully");
  }

  private async redirectByRole(role: Role) {
    switch (role) {
      case Role.ADMIN:
        await this.router.push("/admin/dashboard");
        break;
      case Role.TEACHER:
        await this.router.push("/teacher/dashboard");
        break;
      case Role.STUDENT:
        await this.router.push("/student/dashboard");
        break;
      default:
        await this.router.push("/auth/login");
    }
  }
}
