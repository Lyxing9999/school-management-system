import type { Ref } from "vue";
export enum UserRole {
  Admin = "admin",
  Teacher = "teacher",
  Student = "student",
}
export interface AuthUser {
  id?: string;
  username: string;
  email?: string | null;
  role: UserRole;
  token?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  user: AuthUser;
  access_token: string;
}

export interface AuthContext {
  user: AuthUser | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isAuthenticated: Ref<boolean>;
}
