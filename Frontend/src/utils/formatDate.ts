import dayjs from "dayjs";
import { KH_TZ } from "./date";

export function formatDate(raw: string | null | undefined, format?: string) {
  if (!raw) return "N/A";

  // If no timezone info, assume UTC (backend timestamps are typically UTC)
  const hasTZ = /Z$|[+-]\d{2}:\d{2}$/.test(raw);

  const d = hasTZ ? dayjs(raw) : dayjs.utc(raw);

  return d.isValid()
    ? d.tz(KH_TZ).format(format || "MMM D, YYYY, h:mm A")
    : "Invalid Date";
}
