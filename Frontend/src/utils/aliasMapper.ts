export type AliasMap = Record<string, string>;

export function mapAliases<T>(data: any, aliasMap: AliasMap): T {
  const result: any = {};
  for (const key in aliasMap) {
    result[key] = data[aliasMap[key]];
  }
  return result as T;
}

export function mapAliasList<T>(dataList: any[], aliasMap: AliasMap): T[] {
  return dataList.map((data) => mapAliases<T>(data, aliasMap));
}
