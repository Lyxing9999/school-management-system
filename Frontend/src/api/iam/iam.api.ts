import type { AxiosInstance } from "axios";
import type {
  UserRegisterForm,
  UserLoginForm,
  UserLoginResponse,
  UserRegisterResponse,
  MeResponse,
  RefreshApiResponse,
} from "~/api/iam/iam.dto";

export class AuthApi {
  constructor(private $api: AxiosInstance, private baseURL = "/api/iam") {}

  async registerUser(form: UserRegisterForm) {
    return this.$api
      .post<UserRegisterResponse>(`${this.baseURL}/register`, form)
      .then((r) => r.data);
  }

  async login(form: UserLoginForm) {
    return this.$api
      .post<UserLoginResponse>(`${this.baseURL}/login`, form)
      .then((r) => r.data);
  }

  async refresh() {
    return this.$api
      .post<RefreshApiResponse>(`${this.baseURL}/refresh`)
      .then((r) => r.data);
  }

  async me() {
    return this.$api.get<MeResponse>(`${this.baseURL}/me`).then((r) => r.data);
  }

  async logout() {
    return this.$api.post(`${this.baseURL}/logout`).then((r) => r.data);
  }
}
