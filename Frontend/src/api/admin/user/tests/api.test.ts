import { describe, it, expect, vi, beforeEach } from "vitest";
import { UserApi } from "../api";
import type { AxiosInstance } from "axios";
import { Role } from "~/api/types/enums/role.enum";
import type { AdminCreateUser, AdminUpdateUser } from "../dto";

describe("UserApi", () => {
  let mockAxios: AxiosInstance;
  let userApi: UserApi;

  beforeEach(() => {
    mockAxios = {
      get: vi.fn(),
      post: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
    } as unknown as AxiosInstance;

    userApi = new UserApi(mockAxios);
  });

  // -------------------------
  // Success tests
  // -------------------------
  it("getUsers should call GET with correct params for single role", async () => {
    const mockData = { data: { users: [], total: 0 } };
    (mockAxios.get as any).mockResolvedValue(mockData);

    const res = await userApi.getUsers(Role.STUDENT, 1, 10);

    expect(mockAxios.get).toHaveBeenCalledWith("/api/admin/users", {
      params: { role: Role.STUDENT, page: 1, page_size: 10 },
    });
    expect(res).toEqual(mockData.data);
  });

  it("getUserPage should call GET with correct params for multiple roles", async () => {
    const mockData = { data: { users: [], total: 0 } };
    (mockAxios.get as any).mockResolvedValue(mockData);

    const roles = [Role.STUDENT, Role.TEACHER];
    const res = await userApi.getUserPage(roles, 2, 5);

    expect(mockAxios.get).toHaveBeenCalledWith("/api/admin/users", {
      params: { "role[]": roles, page: 2, page_size: 5 },
    });
    expect(res).toEqual(mockData.data);
  });

  it("createUser should call POST with correct payload", async () => {
    const payload: AdminCreateUser = {
      name: "Jane",
      email: "jane@example.com",
      role: Role.STUDENT,
      password: "123456",
    };
    const mockData = { data: { id: "1", ...payload } };
    (mockAxios.post as any).mockResolvedValue(mockData);

    const res = await userApi.createUser(payload);

    expect(mockAxios.post).toHaveBeenCalledWith("/api/admin/users", payload);
    expect(res).toEqual(mockData.data);
  });

  it("updateUser should call PATCH with correct ID and payload", async () => {
    const payload: AdminUpdateUser = { name: "Jane Updated" };
    const mockData = { data: { id: "1", ...payload } };
    (mockAxios.patch as any).mockResolvedValue(mockData);

    const res = await userApi.updateUser("1", payload);

    expect(mockAxios.patch).toHaveBeenCalledWith("/api/admin/users/1", payload);
    expect(res).toEqual(mockData.data);
  });

  it("deleteUser should call DELETE with correct ID", async () => {
    const mockData = { data: { id: "1", deleted: true } };
    (mockAxios.delete as any).mockResolvedValue(mockData);

    const res = await userApi.deleteUser("1");

    expect(mockAxios.delete).toHaveBeenCalledWith("/api/admin/users/1");
    expect(res).toEqual(mockData.data);
  });

  // -------------------------
  // Error / raise tests
  // -------------------------
  it("getUserPage should handle 404 error", async () => {
    (mockAxios.get as any).mockRejectedValue({
      response: { status: 404, data: "Not Found" },
    });

    await expect(userApi.getUserPage(Role.STUDENT, 1, 10)).rejects.toEqual({
      response: { status: 404, data: "Not Found" },
    });
  });

  it("createUser should handle validation error (Pydantic)", async () => {
    const payload: AdminCreateUser = {
      name: "",
      email: "invalid",
      role: Role.STUDENT,
      password: "123",
    };
    (mockAxios.post as any).mockRejectedValue({
      response: { status: 422, data: { field_errors: { email: "invalid" } } },
    });

    await expect(userApi.createUser(payload)).rejects.toEqual({
      response: { status: 422, data: { field_errors: { email: "invalid" } } },
    });
  });

  it("createUser should handle email already exists error", async () => {
    const payload: AdminCreateUser = {
      name: "Jane",
      email: "already@used.com",
      role: Role.STUDENT,
      password: "123456",
    };
    (mockAxios.post as any).mockRejectedValue({
      response: {
        status: 409,
        data: { message: "Email 'already@used.com' already exists" },
      },
    });

    await expect(userApi.createUser(payload)).rejects.toEqual({
      response: {
        status: 409,
        data: { message: "Email 'already@used.com' already exists" },
      },
    });
  });

  it("createUser should handle username already exists error", async () => {
    const payload: AdminCreateUser = {
      name: "Jane",
      email: "jane@new.com",
      role: Role.STUDENT,
      password: "123456",
      username: "takenUsername",
    };
    (mockAxios.post as any).mockRejectedValue({
      response: {
        status: 409,
        data: { message: "Username 'takenUsername' already exists" },
      },
    });

    await expect(userApi.createUser(payload)).rejects.toEqual({
      response: {
        status: 409,
        data: { message: "Username 'takenUsername' already exists" },
      },
    });
  });

  it("updateUser should handle server error", async () => {
    const payload: AdminUpdateUser = { name: "Jane Updated" };
    (mockAxios.patch as any).mockRejectedValue({
      response: { status: 500, data: "Server Error" },
    });

    await expect(userApi.updateUser("1", payload)).rejects.toEqual({
      response: { status: 500, data: "Server Error" },
    });
  });

  it("deleteUser should handle unauthorized error", async () => {
    (mockAxios.delete as any).mockRejectedValue({
      response: { status: 401, data: "Unauthorized" },
    });

    await expect(userApi.deleteUser("1")).rejects.toEqual({
      response: { status: 401, data: "Unauthorized" },
    });
  });
});
