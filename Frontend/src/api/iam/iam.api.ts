import type { AxiosInstance } from "axios";
import type {
  UserRegister,
  UserLoginForm,
  UserLoginResponse,
  UserRegisterResponse,
} from "~/api/iam/iam.dto";

export class AuthApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/iam") {}

  async registerUser(form: UserRegister): Promise<UserRegisterResponse> {
    const response = await this.$api.post<UserRegisterResponse>(
      `${this.baseURL}/register`,
      form
    );

    return response.data;
  }
  async login(form: UserLoginForm): Promise<UserLoginResponse> {
    const response = await this.$api.post<UserLoginResponse>(
      `${this.baseURL}/login`,
      form
    );
    return response.data;
  }

  loginWithGoogle(apiBase: string) {
    window.location.href = `${apiBase}/auth/google/login`;
  }
  // TODO return current profile
  // change password

  async getMyProfile() {
    const response = await this.$api.get<UserLoginResponse>(
      `${this.baseURL}/profile`
    );
    return response.data;
  }
}
