import type { AxiosInstance } from "axios";
import type {
  UserRegisterForm,
  UserLoginForm,
  UserLoginResponse,
  UserRegisterResponse,
  RefreshApiResponse,
  ResetPasswordConfirmPayload,
  ResetPasswordConfirmResponse,
  ChangePasswordForm,
  ChangePasswordResponse,
  UpdateMePayload,
} from "~/api/iam/iam.dto";
import type { UserBaseDataDTO as MeResponse } from "~/api/types/user.dto";
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

  async getMe() {
    return this.$api.get<MeResponse>(`${this.baseURL}/me`).then((r) => r.data);
  }

  async logout() {
    return this.$api.post(`${this.baseURL}/logout`).then((r) => r.data);
  }

  async confirmResetPassword(payload: ResetPasswordConfirmPayload) {
    return this.$api
      .post<ResetPasswordConfirmResponse>(
        `${this.baseURL}/reset-password/confirm`,
        payload
      )
      .then((r) => r.data);
  }

  async changePassword(form: ChangePasswordForm) {
    return this.$api
      .post<ChangePasswordResponse>(`${this.baseURL}/change-password`, form)
      .then((r) => r.data);
  }
  async updateMe(payload: UpdateMePayload) {
    return this.$api
      .patch<MeResponse>(`${this.baseURL}/me`, payload)
      .then((r) => r.data);
  }
}
