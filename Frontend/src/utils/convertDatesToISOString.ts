export function convertDatesToISOString(obj: any): any {
  if (Array.isArray(obj)) {
    return obj.map(convertDatesToISOString);
  } else if (obj !== null && typeof obj === "object") {
    const result: any = {};
    for (const key in obj) {
      const val = obj[key];
      if (val instanceof Date) {
        result[key] = val.toISOString(); // convert Date to ISO string (UTC)
      } else {
        result[key] = convertDatesToISOString(val);
      }
    }
    return result;
  }
  return obj;
}
