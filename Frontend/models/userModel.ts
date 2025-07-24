import type { User } from "~/types/models/User";
import { Role } from "~/types/models/User";

export class UserModel implements User {
  _id: string;
  username: string;
  email?: string;
  password?: string;
  role: Role;
  createdAt?: string;
  updatedAt?: string;

  constructor(data: Partial<User> = {}) {
    this._id = data._id || "";
    this.role = data.role ?? Role.STUDENT;
    this.username = data.username?.trim() ?? "";
    this.email = data.email?.trim();
    this.password = data.password?.trim();
    this.createdAt =
      data.created_at?.trim() || data.createdAt?.trim() || undefined;
    this.updatedAt =
      data.updated_at?.trim() || data.updatedAt?.trim() || undefined;
  }

  toDict(includePassword = false): Record<string, any> {
    const result: Record<string, any> = {
      role: this.role,
      username: this.username,
    };

    if (this._id) result._id = this._id;
    if (this.email) result.email = this.email;
    if (this.createdAt) result.created_at = this.createdAt;
    if (this.updatedAt) result.updated_at = this.updatedAt;
    if (includePassword && this.password) result.password = this.password;

    return result;
  }
}
