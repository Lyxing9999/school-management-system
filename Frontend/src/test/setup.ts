import { vi } from "vitest";
import { config } from "@vue/test-utils";

// Mock your stores and services
vi.mock("~/stores/userStore", () => ({
  useUserStore: vi.fn(() => ({
    users: [],
    fetchUsers: vi.fn().mockResolvedValue([]),
    updateUserPatch: vi.fn().mockResolvedValue({}),
  })),
}));

vi.mock("~/services/userService", () => ({
  UserService: vi.fn(() => ({
    deleteUser: vi.fn().mockResolvedValue({}),
    updateUser: vi.fn().mockResolvedValue({}),
    getUserDetails: vi.fn().mockResolvedValue({}),
  })),
}));

vi.mock("~/composables/common/useMessage", () => ({
  useMessage: vi.fn(() => ({
    showSuccess: vi.fn(),
    showInfo: vi.fn(),
    showError: vi.fn(),
  })),
}));

// Mock your components
vi.mock("~/components/Base/MultiTypeEditCell.vue", () => ({
  default: { name: "MultiTypeEditCell" },
}));

vi.mock("~/components/Base/CustomButton.vue", () => ({
  default: { name: "CustomButton" },
}));

vi.mock("~/components/Base/EditableColumn.vue", () => ({
  default: { name: "EditableColumn" },
}));

vi.mock("~/components/Base/UserDetailDialog.vue", () => ({
  default: { name: "UserDetailDialog" },
}));

vi.mock("~/components/admin/CreateUserForm.vue", () => ({
  default: { name: "CreateUserForm" },
}));

vi.mock("~/components/admin/AdminAttendanceDict.vue", () => ({
  default: { name: "AdminAttendanceDict" },
}));

// Mock utility functions
vi.mock("~/utils/unflatten", () => ({
  unflatten: vi.fn((obj) => obj),
}));

// Mock constants
vi.mock("~/constants/fields/adminFields", () => ({
  adminFields: [],
}));

vi.mock("~/constants/fields/teacherFields", () => ({
  teacherFields: [],
}));

vi.mock("~/constants/fields/studentFields", () => ({
  studentFields: [],
}));

// Mock models
vi.mock("~/models/userModel", () => ({
  UserModel: class UserModel {
    constructor(data: any) {
      Object.assign(this, data);
    }
  },
}));

// Mock errors
vi.mock("~/errors/UserStoreError", () => ({
  UserStoreError: class UserStoreError extends Error {
    code: string;
    constructor(message: string, code: string) {
      super(message);
      this.code = code;
    }
  },
}));

// Configure Vue Test Utils
config.global.stubs = {
  "el-skeleton": true,
  "el-table": true,
  "el-table-column": true,
  "el-row": true,
  "el-col": true,
  "el-tag": true,
  "el-pagination": true,
  "el-dialog": true,
};
