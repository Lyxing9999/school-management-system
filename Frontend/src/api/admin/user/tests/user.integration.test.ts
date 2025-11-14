/**
 * @vitest-environment node
 */
import { describe, it, expect, beforeAll } from "vitest";
import axios, { type AxiosInstance } from "axios";
import { Role } from "~/api/types/enums/role.enum";

const API_BASE = "http://localhost:5001/api/admin";
let api: AxiosInstance;
let token: string;
let createdUserId: string;

beforeAll(async () => {
  // Login as admin
  const loginRes = await axios.post("http://localhost:5001/api/iam/login", {
    email: "admin@gmail.com",
    password: "12345678",
  });

  console.log("Login response:", loginRes.data);

  token = loginRes.data?.data?.access_token;
  if (!token) throw new Error("Login failed, no token received");

  api = axios.create({
    baseURL: API_BASE,
    headers: { Authorization: `Bearer ${token}` },
  });
});

describe("UserApi Real Backend with Admin Login", () => {
  it("should create a new user", async () => {
    const payload = {
      email: "student1@test.com",
      username: "Student1",
      password: "12345678",
      role: "student", // must match backend expected value
    };

    const res = await api.post("/users", payload);

    expect(res.status).toBe(200);
    expect(res.data).toHaveProperty("id");

    createdUserId = res.data.id;
  });

  it("should get users with role STUDENT", async () => {
    const res = await api.get("/users", {
      params: { role: "student", page: 1, page_size: 10 },
    });

    expect(res.status).toBe(200);
    expect(res.data.data.users).toEqual(
      expect.arrayContaining([expect.objectContaining({ role: "student" })])
    );
  });

  it("should update user info", async () => {
    const payload = { username: "UpdatedStudent1" };

    const res = await api.patch(`/users/${createdUserId}`, payload);

    expect(res.status).toBe(200);
    expect(res.data.username).toBe("UpdatedStudent1");
  });

  it("should delete user", async () => {
    const res = await api.delete(`/users/${createdUserId}`);

    expect(res.status).toBe(200);
    expect(res.data.deleted).toBe(true);
  });
});
