export enum Role {
  TEACHER = "teacher",
  STUDENT = "student",
  ADMIN = "admin",
}

export interface User {
  _id: string;
  role: Role;
  username: string;
  email?: string;
  password?: string;
  createdAt?: string;
  created_at?: string;
  updatedAt?: string;
  updated_at?: string;
}
