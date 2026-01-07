import type { GradeEnriched } from "~/api/teacher/dto";

export function getLifecycleCreatedAt(row: GradeEnriched): string | null {
  return row?.lifecycle?.created_at ?? row?.lifecycle?.created_at ?? null;
}

export function pickStudentEn(row: GradeEnriched): string {
  return (
    row?.student_name_en?.trim() ||
    row?.student_name?.trim() ||
    row?.student_name_kh?.trim() ||
    "-"
  );
}

export function pickStudentKh(row: GradeEnriched): string {
  return (
    row?.student_name_kh?.trim() ||
    row?.student_name?.trim() ||
    row?.student_name_en?.trim() ||
    "-"
  );
}
