import type { AxiosInstance } from "axios";
import type {
  UserLoginForm,
  UserRegisterForm,
  UserRegisterResponseDTO,
  UserLoginResponseDTO,
} from "~/types";

export class AuthApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/auth") {}

  async registerUser(form: UserRegisterForm): Promise<UserRegisterResponseDTO> {
    const response = await this.$api.post<UserRegisterResponseDTO>(
      `${this.baseURL}/register`,
      form
    );
    return response.data;
  }
  async login(form: UserLoginForm): Promise<UserLoginResponseDTO> {
    const response = await this.$api.post<UserLoginResponseDTO>(
      `${this.baseURL}/login`,
      form
    );
    return response.data;
  }

  loginWithGoogle(apiBase: string) {
    window.location.href = `${apiBase}/auth/google/login`;
  }
}
