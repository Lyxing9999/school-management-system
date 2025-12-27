import type { AdminDashboardFilterDTO } from "../api/dashboard.dto";

export type TermValue = "" | "S1" | "S2";
export type DateRange = [Date, Date] | null;

export const termOptions: Array<{ label: string; value: TermValue }> = [
  { label: "All terms", value: "" },
  { label: "Semester 1", value: "S1" },
  { label: "Semester 2", value: "S2" },
];

export function formatDateParam(d: Date): string {
  // "YYYY-MM-DD"
  return d.toISOString().slice(0, 10);
}

export function buildDashboardFilters(args: {
  dateRange: DateRange;
  term: TermValue;
}): AdminDashboardFilterDTO {
  const filters: AdminDashboardFilterDTO = {};

  if (args.dateRange) {
    const [start, end] = args.dateRange;
    filters.date_from = formatDateParam(start);
    filters.date_to = formatDateParam(end);
  }

  if (args.term) {
    filters.term = args.term;
  }

  return filters;
}
