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



export function normalizeRow<T extends Record<string, any>>(row: T): T & { id: string } {
  return { ...row, id: row.id ?? row._id?.toString?.() ?? crypto.randomUUID() };
}

export function safeId(row: { id?: string | number; _id?: any }): string {
  return row.id?.toString() ?? row._id?.toString?.() ?? crypto.randomUUID();
}

export function getKey(id: string | number | undefined | null): string {
  if (id === undefined || id === null)
    return "__undefined_id__" + Math.random().toString(36).substr(2, 6);
  return String(id);
}