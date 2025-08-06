import { mapAliases, mapAliasList, type AliasMap } from "~/utils/aliasMapper";
import type { AdminFindUserDataDTO } from "./admin_user_dto";

const AdminUserAliasMap: AliasMap = {
  id: "_id",
  username: "username",
  role: "role",
  email: "email",
  created_by: "created_by_admin_id",
  updated_by: "updated_by_admin_id",
  deleted_by: "deleted_by_admin_id",
};

export function mapAdminUser<T = AdminFindUserDataDTO>(data: any): T {
  return mapAliases<T>(data, AdminUserAliasMap);
}

export function mapAdminUserList<T = AdminFindUserDataDTO>(
  dataList: any[]
): T[] {
  return mapAliasList<T>(dataList, AdminUserAliasMap);
}
