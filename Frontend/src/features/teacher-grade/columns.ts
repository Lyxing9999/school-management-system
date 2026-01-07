import { h } from "vue";
import type { ColumnConfig } from "~/components/types/tableEdit";
import type { GradeEnriched } from "~/api/teacher/dto";

import ScoreTag from "./cells/ScoreTag.vue";
import GradeTypeTag from "./cells/GradeTypeTag.vue";
import DateTimeCell from "./cells/DateTimeCell.vue";

import { getLifecycleCreatedAt, pickStudentEn, pickStudentKh } from "./utils";

type BuildColumnsArgs = {
  onEdit: (row: GradeEnriched) => void;
  onDelete: (row: GradeEnriched) => void;
};

const cellText = (text: string) =>
  h("div", { class: "cell-text truncate" }, text);

export function buildTeacherGradeColumns(
  args: BuildColumnsArgs
): ColumnConfig<GradeEnriched>[] {
  return [
    {
      key: "student_en",
      label: "Student EN",
      minWidth: 200,
      render: (row) => cellText(pickStudentEn(row)),
    },
    {
      key: "student_kh",
      label: "Student KH",
      minWidth: 200,
      customClass: "col-hide-md",
      render: (row) => cellText(pickStudentKh(row)),
    },

    {
      key: "subject_label",
      label: "Subject",
      field: "subject_label",
      minWidth: 240,
      render: (row) => cellText(row.subject_label || "-"),
    },
    {
      key: "score",
      label: "Score",
      field: "score",
      minWidth: 120,
      align: "center",
      render: (row) => h(ScoreTag, { score: row.score }),
    },
    {
      key: "type",
      label: "Type",
      field: "type",
      minWidth: 140,
      align: "center",
      customClass: "col-hide-sm",
      render: (row) => h(GradeTypeTag, { type: row.type }),
    },

    {
      key: "teacher_name",
      label: "Teacher",
      minWidth: 200,
      render: (row) => cellText(row.teacher_name || "-"),
    },
    {
      key: "term",
      label: "Term",
      field: "term",
      minWidth: 120,
      align: "center",
      customClass: "col-hide-md",
      render: (row) => h("span", {}, row.term || "-"),
    },
    {
      key: "created_at",
      label: "Created At",
      minWidth: 170,
      customClass: "col-hide-md",
      render: (row) => h(DateTimeCell, { value: getLifecycleCreatedAt(row) }),
    },

    {
      label: "Actions",
      slotName: "operation",
      operation: true,
      fixed: "right",
      width: "220px",
      align: "center",
    },
  ];
}
