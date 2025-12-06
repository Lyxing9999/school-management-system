import { describe, it, expect, vi, beforeEach } from "vitest";
import { UserService } from "../user.service";
import { Role } from "~/api/types/enums/role.enum";
import type { AdminUpdateUser, AdminCreateUser } from "../user.dto";

describe("UserService", () => {
  let service: UserService;
  let mockSafeApiCall: any;
  let mockApi: any;

  beforeEach(() => {
    // Mock API methods
    mockApi = {
      getUsers: vi.fn(),
      createUser: vi.fn(),
      updateUser: vi.fn(),
      deleteUser: vi.fn(),
    };

    // Mock safeApiCall
    mockSafeApiCall = vi.fn(async (fn) => fn());

    // Inject mockApi and mockSafeApiCall
    service = new UserService(mockApi);
    service["safeApiCall"] = mockSafeApiCall;
  });

  it("getUsers should return data from safeApiCall", async () => {
    const mockData = { users: [{ id: "1", name: "Jane" }], total: 1 };
    mockApi.getUsers.mockResolvedValue({ data: mockData });

    const res = await service.getUsers(Role.STUDENT, 1, 10);

    expect(mockSafeApiCall).toHaveBeenCalled();
    expect(res).toEqual(mockData);
  });

  it("createUser should return data from safeApiCall", async () => {
    const payload = {
      name: "Jane",
      email: "jane@example.com",
      role: Role.STUDENT,
      password: "123456",
    };
    const mockData = { id: "1", ...(payload as unknown as AdminCreateUser) };
    mockApi.createUser.mockResolvedValue({ data: mockData });

    const res = await service.createUser(payload as unknown as AdminCreateUser);

    expect(mockSafeApiCall).toHaveBeenCalled();
    expect(res).toEqual(mockData);
  });

  it("updateUser should return data from safeApiCall", async () => {
    const payload = { name: "Jane Updated" };
    const mockData = { id: "1", ...payload };
    mockApi.updateUser.mockResolvedValue({ data: mockData });

    const res = await service.updateUser("1", payload as AdminUpdateUser);

    expect(mockSafeApiCall).toHaveBeenCalled();
    expect(res).toEqual(mockData);
  });

  it("deleteUser should return data from safeApiCall", async () => {
    const mockData = { id: "1", deleted: true };
    mockApi.deleteUser.mockResolvedValue({ data: mockData });

    const res = await service.deleteUser("1");

    expect(mockSafeApiCall).toHaveBeenCalled();
    expect(res).toEqual(mockData);
  });
});
