import {
  useApiUtils,
  type ApiCallOptions,
} from "~/composables/system/useApiUtils";

import type {
  HrEmployeeDTO,
  HrEmployeeAccountDTO,
  HrEmployeeWithAccountDTO,
  HrEmployeeWithAccountSummaryPaginatedDTO,
  HrCreateEmployeeDTO,
  HrUpdateEmployeeDTO,
  HrCreateEmployeeAccountDTO,
  HrEmployeeOnboardDTO,
  ListEmployeesParams,
  ListEmployeeAccountsParams,
  HrLinkEmployeeAccountDTO,
  HrEmployeeAccountPaginatedDTO,
  HrUpdateEmployeeAccountDTO,
  HrPasswordResetResponse,
} from "./dto";
import { EmployeeApi } from "./api";
import { Status } from "../../types/enums/status.enum";
export class EmployeeService {
  private readonly callApi = useApiUtils().callApi;

  constructor(private readonly employeeApi: EmployeeApi) {}

  async getEmployeesWithAccounts(
    params?: ListEmployeesParams,
    options?: ApiCallOptions,
  ): Promise<HrEmployeeWithAccountSummaryPaginatedDTO> {
    const data = await this.callApi<HrEmployeeWithAccountSummaryPaginatedDTO>(
      () => this.employeeApi.getEmployeesWithAccounts(params),
      options,
    );
    return data!;
  }

  async getEmployee(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<HrEmployeeDTO>(
      () => this.employeeApi.getEmployee(id),
      options,
    );
    return data!;
  }

  async getMyEmployee(options?: ApiCallOptions) {
    const data = await this.callApi<HrEmployeeDTO>(
      () => this.employeeApi.getMyEmployee(),
      options,
    );
    return data!;
  }

  async getEmployeeAccount(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<HrEmployeeAccountDTO | null>(
      () => this.employeeApi.getEmployeeAccount(id),
      options,
    );
    return data!;
  }

  async createEmployee(payload: HrCreateEmployeeDTO, options?: ApiCallOptions) {
    const data = await this.callApi<HrEmployeeDTO>(
      () => this.employeeApi.createEmployee(payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async updateEmployee(
    id: string,
    payload: HrUpdateEmployeeDTO,
    options?: ApiCallOptions,
  ) {
    const data = await this.callApi<HrEmployeeDTO>(
      () => this.employeeApi.updateEmployee(id, payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async softDeleteEmployee(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<void>(
      () => this.employeeApi.softDeleteEmployee(id),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async restoreEmployee(id: string, options?: ApiCallOptions) {
    const data = await this.callApi<void>(
      () => this.employeeApi.restoreEmployee(id),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async createAccount(
    employeeId: string,
    payload: HrCreateEmployeeAccountDTO,
    options?: ApiCallOptions,
  ) {
    const data = await this.callApi<HrEmployeeWithAccountDTO>(
      () => this.employeeApi.createAccount(employeeId, payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async onboardEmployee(
    payload: HrEmployeeOnboardDTO,
    options?: ApiCallOptions,
  ) {
    const data = await this.callApi<HrEmployeeWithAccountDTO>(
      () => this.employeeApi.onboardEmployee(payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async softDeleteEmployeeAccount(
    employeeId: string,
    options?: ApiCallOptions,
  ) {
    const data = await this.callApi<HrEmployeeAccountDTO>(
      () => this.employeeApi.softDeleteEmployeeAccount(employeeId),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async restoreEmployeeAccount(employeeId: string, options?: ApiCallOptions) {
    const data = await this.callApi<HrEmployeeAccountDTO>(
      () => this.employeeApi.restoreEmployeeAccount(employeeId),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }
  async getEmployeeAccounts(
    params?: ListEmployeeAccountsParams,
    options?: ApiCallOptions,
  ): Promise<HrEmployeeAccountPaginatedDTO> {
    const data = await this.callApi<HrEmployeeAccountPaginatedDTO>(
      () => this.employeeApi.getEmployeeAccounts(params),
      options,
    );
    return data!;
  }

  async linkAccount(
    employeeId: string,
    payload: HrLinkEmployeeAccountDTO,
    options?: ApiCallOptions,
  ) {
    const data = await this.callApi<HrEmployeeDTO>(
      () => this.employeeApi.linkAccount(employeeId, payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async updateEmployeeAccount(
    employeeId: string,
    payload: HrUpdateEmployeeAccountDTO,
    options?: ApiCallOptions,
  ) {
    const data = await this.callApi<HrEmployeeAccountDTO>(
      () => this.employeeApi.updateEmployeeAccount(employeeId, payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }

  async requestEmployeeAccountPasswordReset(
    employeeId: string,
    options?: ApiCallOptions,
  ) {
    const data = await this.callApi<HrPasswordResetResponse>(
      () => this.employeeApi.requestEmployeeAccountPasswordReset(employeeId),
      { showSuccess: false, ...(options ?? {}) },
    );
    return data!;
  }

  async setEmployeeAccountStatus(
    userId: string,
    payload: { status: Status },
    options?: ApiCallOptions,
  ) {
    const data = await this.callApi<{ id: string; status: Status }>(
      () => this.employeeApi.setEmployeeAccountStatus(userId, payload),
      { showSuccess: true, ...(options ?? {}) },
    );
    return data!;
  }
}
