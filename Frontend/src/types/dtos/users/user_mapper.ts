import { mapAliases, mapAliasList, type AliasMap } from "~/utils";
import type { UserResponseDataDTO } from "./user_action_dto";

const UserAliasMap: AliasMap = {
  id: "_id",
  username: "username",
  role: "role",
  email: "email",
};

export function mapUser<T = UserResponseDataDTO>(data: any): T {
  return mapAliases<T>(data, UserAliasMap);
}

export function mapUserList<T = UserResponseDataDTO>(dataList: any[]): T[] {
  return mapAliasList<T>(dataList, UserAliasMap);
}
