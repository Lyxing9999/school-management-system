import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezone);

export const KH_TZ = "Asia/Phnom_Penh";

export function formatDate(raw: string | null | undefined, format?: string) {
  if (!raw) return "N/A";

  const hasTZ = /Z$|[+-]\d{2}:\d{2}$/.test(raw);
  const d = hasTZ ? dayjs(raw) : dayjs.utc(raw);

  return d.isValid()
    ? d.tz(KH_TZ).format(format || "MMM D, YYYY, h:mm A")
    : "Invalid Date";
}
