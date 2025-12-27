export type TopAbsentStudentRow = {
  student_id: string;
  student_name: string;
  absent_count: number;
  class_name: string;
  class_id?: string | null;
  total_records: number;
};

export function normalizeTopAbsentStudents(
  raw: unknown
): TopAbsentStudentRow[] {
  const rows = Array.isArray(raw) ? raw : [];

  return rows.map((r: any) => ({
    student_id: String(r.student_id ?? ""),
    student_name: String(r.student_name ?? "Unknown"),
    absent_count: Number(r.absent_count ?? 0),
    class_id: r.class_id != null ? String(r.class_id) : null,
    class_name: String(r.class_name ?? r.class_label ?? "Unknown"),
    total_records:
      r.total_records != null
        ? Number(r.total_records)
        : Number(r.absent_count ?? 0),
  }));
}
