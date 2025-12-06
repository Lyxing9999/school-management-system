import { describe, it, expect, vi, beforeEach } from "vitest";
import type { AxiosInstance } from "axios";
import { SubjectApi } from "../subject.api";
import type { AdminCreateSubject, AdminUpdateSubject } from "../subject.dto";

describe("SubjectApi", () => {
  let mockAxios: AxiosInstance;
  let subjectApi: SubjectApi;

  beforeEach(() => {
    mockAxios = {
      get: vi.fn(),
      post: vi.fn(),
      patch: vi.fn(),
      delete: vi.fn(),
    } as unknown as AxiosInstance;

    subjectApi = new SubjectApi(mockAxios);
  });

  // ------------------------
  // ✅ SUCCESS TESTS
  // ------------------------

  it("should fetch all subjects", async () => {
    const mockData = { data: { message: "ok", subjects: [] } };
    (mockAxios.get as any).mockResolvedValue(mockData);

    const res = await subjectApi.getSubjects();

    expect(mockAxios.get).toHaveBeenCalledWith("/api/admin/subject");
    expect(res).toEqual(mockData.data);
  });

  it("should fetch subject by id", async () => {
    const mockData = { data: { id: "1", name: "Math" } };
    (mockAxios.get as any).mockResolvedValue(mockData);

    const res = await subjectApi.getSubjectById("1");

    expect(mockAxios.get).toHaveBeenCalledWith("/api/admin/subject/1");
    expect(res).toEqual(mockData.data);
  });

  it("should create subject", async () => {
    const data: AdminCreateSubject = { name: "Science" } as any;
    const mockData = { data: { id: "123", ...data } };
    (mockAxios.post as any).mockResolvedValue(mockData);

    const res = await subjectApi.createSubject(data);

    expect(mockAxios.post).toHaveBeenCalledWith("/api/admin/subject", data);
    expect(res).toEqual(mockData.data);
  });

  it("should update subject", async () => {
    const data: AdminUpdateSubject = { name: "Updated Math" } as any;
    const mockData = { data: { id: "1", ...data } };
    (mockAxios.patch as any).mockResolvedValue(mockData);

    const res = await subjectApi.updateSubject("1", data);

    expect(mockAxios.patch).toHaveBeenCalledWith("/api/admin/subject/1", data);
    expect(res).toEqual(mockData.data);
  });

  it("should delete subject", async () => {
    const mockData = { data: { message: "deleted" } };
    (mockAxios.delete as any).mockResolvedValue(mockData);

    const res = await subjectApi.deleteSubject("1");

    expect(mockAxios.delete).toHaveBeenCalledWith("/api/admin/subject/1");
    expect(res).toEqual(mockData.data);
  });

  // ------------------------
  // ⚠️ ERROR TESTS (simulate backend raises)
  // ------------------------

  it("should handle 404 when subject not found", async () => {
    (mockAxios.get as any).mockRejectedValue({
      response: { status: 404, data: { message: "Subject not found" } },
    });

    await expect(subjectApi.getSubjectById("invalid-id")).rejects.toMatchObject(
      {
        response: { status: 404, data: { message: "Subject not found" } },
      }
    );

    expect(mockAxios.get).toHaveBeenCalledWith("/api/admin/subject/invalid-id");
  });

  it("should handle validation error on create", async () => {
    (mockAxios.post as any).mockRejectedValue({
      response: { status: 400, data: { message: "Invalid subject data" } },
    });

    const data: AdminCreateSubject = { name: "" } as any;

    await expect(subjectApi.createSubject(data)).rejects.toMatchObject({
      response: { status: 400, data: { message: "Invalid subject data" } },
    });

    expect(mockAxios.post).toHaveBeenCalledWith("/api/admin/subject", data);
  });

  it("should handle server error on update", async () => {
    (mockAxios.patch as any).mockRejectedValue({
      response: { status: 500, data: { message: "Internal server error" } },
    });

    const data: AdminUpdateSubject = { name: "New Name" } as any;

    await expect(subjectApi.updateSubject("1", data)).rejects.toMatchObject({
      response: { status: 500, data: { message: "Internal server error" } },
    });

    expect(mockAxios.patch).toHaveBeenCalledWith("/api/admin/subject/1", data);
  });

  it("should handle unauthorized delete", async () => {
    (mockAxios.delete as any).mockRejectedValue({
      response: { status: 403, data: { message: "Forbidden" } },
    });

    await expect(subjectApi.deleteSubject("1")).rejects.toMatchObject({
      response: { status: 403, data: { message: "Forbidden" } },
    });

    expect(mockAxios.delete).toHaveBeenCalledWith("/api/admin/subject/1");
  });
});
