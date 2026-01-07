export function unflatten(obj: Record<string, any>) {
  const result: Record<string, any> = {};
  for (const flatKey in obj) {
    const keys = flatKey.split(".");
    keys.reduce((acc, key, index) => {
      if (index === keys.length - 1) {
        acc[key] = obj[flatKey];
        return;
      }
      if (!acc[key]) acc[key] = {};
      return acc[key];
    }, result);
  }
  return result;
}
