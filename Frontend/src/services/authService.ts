import { jwtDecode } from "jwt-decode";
import { useMessage } from "~/composables/common/useMessage";
import { useRouter } from "nuxt/app";
import { useAuthStore } from "~/stores/authStore";
import { AuthApi } from "~/api/auth/auth.api";
import { useApiUtils } from "~/utils/useApiUtils";
import { Role } from "~/api/types/enums/role.enum";
import type {
  UserRegisterForm,
  UserLoginForm,
  AuthDataDTO,
} from "~/api/auth/auth.dto";
import type { UserBaseDataDTO } from "~/api/types/userBase";

export class AuthService {
  private router = useRouter();
  private authStore = useAuthStore();
  private safeApiCall = useApiUtils().safeApiCall;
  private message = useMessage();
  constructor(private authApi: AuthApi) {}

  private validateCredentials(form: UserRegisterForm | UserLoginForm): boolean {
    if (!form.email || !form.password) {
      this.message.showWarning("Please fill in all fields");
      return false;
    }
    return true;
  }

  async register(form: UserRegisterForm): Promise<AuthDataDTO | null> {
    if (!this.validateCredentials(form)) return null;

    const { data } = await this.safeApiCall<AuthDataDTO>(
      this.authApi.registerUser(form),
      {
        showSuccessNotification: true,
        showErrorNotification: true,
      }
    );
    if (!data) return null;
    await this.router.push("/auth/login");
    return data;
  }

  async login(form: UserLoginForm): Promise<void | null> {
    if (!this.validateCredentials(form)) return null;

    const { data } = await this.safeApiCall<AuthDataDTO>(
      this.authApi.login(form),
      {
        showErrorNotification: true,
        showSuccessNotification: true,
      }
    );
    if (!data) return;
    const token = data.access_token;
    if (!token) {
      this.message.showError("Invalid response from server: no token");
      return;
    }
    const decodedUser = jwtDecode(token) as UserBaseDataDTO;
    this.authStore.login(token, decodedUser);
    await this.redirectByRole(decodedUser.role);
  }

  // loginWithGoogle() {
  //   this.authApi.loginWithGoogle(this.authApi);
  // }

  logout() {
    this.authStore.logout();
    this.router.push("/auth/login");
    this.message.showSuccess("Logged out successfully");
  }

  private async redirectByRole(role: Role) {
    switch (role) {
      case Role.ADMIN:
        await this.router.push("/admin/dashboard");
        break;
      case Role.FRONT_OFFICE:
        await this.router.push("/front-office/dashboard");
        break;
      case Role.ACADEMIC:
        await this.router.push("/academic/dashboard");
        break;
      case Role.FINANCE:
        await this.router.push("/finance/dashboard");
        break;
      case Role.PARENT:
        await this.router.push("/parent/dashboard");
        break;
      case Role.TEACHER:
        await this.router.push("/teacher/dashboard");
        break;
      case Role.STUDENT:
        await this.router.push("/student/dashboard");
        break;
      case Role.HR:
        await this.router.push("/hr/dashboard");
        break;
      default:
        await this.router.push("/auth/login");
    }
  }
}
