export function flatten(
  obj: Record<string, any>,
  parentKey = "",
  result: Record<string, any> = {}
) {
  for (const key in obj) {
    if (!obj.hasOwnProperty(key)) continue;
    const fullKey = parentKey ? `${parentKey}.${key}` : key;
    const value = obj[key];

    if (value && typeof value === "object" && !Array.isArray(value)) {
      // recursively flatten nested objects
      flatten(value, fullKey, result);
    } else {
      result[fullKey] = value;
    }
  }
  return result;
}
