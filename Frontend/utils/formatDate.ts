import dayjs from "dayjs";

export function formatDate(raw: string | null | undefined) {
  if (!raw) return "N/A";
  return dayjs(raw).isValid()
    ? dayjs(raw).format("MMM D, YYYY, h:mm A")
    : "Invalid Date";
}
