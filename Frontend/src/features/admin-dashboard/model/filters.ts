// features/admin-dashboard/model/filters.ts

export type DateRange = [Date, Date] | null;

export type DashboardFiltersInput = {
  dateRange: DateRange;
};

function formatDateParam(d: Date): string {
  // UTC date-only (stable for API)
  const yyyy = d.getUTCFullYear();
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export function buildDashboardFilters(input: DashboardFiltersInput) {
  const params: Record<string, string> = {};
  const { dateRange } = input;

  if (dateRange) {
    const [start, end] = dateRange;
    params.date_from = formatDateParam(start);
    params.date_to = formatDateParam(end);
  }

  return params;
}
export function normalizeDateRange(v: unknown): DateRange {
  if (!v || !Array.isArray(v) || v.length !== 2) return null;
  const [a, b] = v;
  if (!(a instanceof Date) || !(b instanceof Date)) return null;
  return [a, b];
}
