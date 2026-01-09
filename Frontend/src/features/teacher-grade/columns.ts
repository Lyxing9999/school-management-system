import { h, type VNodeChild } from "vue";
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

/** Plain text cell with optional muted (disabled-looking) style */
const cellText = (text: string, muted = false) =>
  h(
    "div",
    {
      class: ["cell-text", "truncate", muted ? "cell-text--muted" : ""]
        .filter(Boolean)
        .join(" "),
      title: text || "", // small UX: hover shows full text
    },
    text
  );

/** Wrap content so column-level muting affects component internals consistently */
const mutedWrap = (child: VNodeChild) =>
  h("div", { class: "cell-muted-wrap" }, [child]);

export function buildTeacherGradeColumns(
  args: BuildColumnsArgs
): ColumnConfig<GradeEnriched>[] {
  return [
    // Student EN
    {
      key: "student_en",
      field: "student_en" as any,
      label: "Student EN",
      minWidth: 220,
      showOverflowTooltip: true,
      render: (row) => cellText(pickStudentEn(row) || "—"),
    },

    // Student KH (responsive hide on md)
    {
      key: "student_kh",
      field: "student_kh" as any,
      label: "Student KH",
      minWidth: 220,
      customClass: "col-hide-md",
      showOverflowTooltip: true,
      render: (row) => cellText(pickStudentKh(row) || "—"),
    },

    // Subject
    {
      key: "subject_label",
      field: "subject_label",
      label: "Subject",
      minWidth: 260,
      showOverflowTooltip: true,
      render: (row) => cellText(row.subject_label || "—"),
    },

    // Score (CENTER)
    {
      key: "score",
      field: "score",
      label: "Score",
      minWidth: 120,
      width: "120px",
      align: "center",
      headerAlign: "center" as any, // depending on your ColumnConfig typing
      render: (row) => h(ScoreTag, { score: row.score }),
    },

    // Type (CENTER)
    {
      key: "type",
      field: "type",
      label: "Type",
      minWidth: 140,
      width: "140px",
      align: "center",
      headerAlign: "center" as any,
      customClass: "col-hide-sm",
      render: (row) => h(GradeTypeTag, { type: row.type }),
    },

    // Teacher
    {
      key: "teacher_name",
      field: "teacher_name" as any,
      label: "Teacher",
      minWidth: 200,
      showOverflowTooltip: true,
      render: (row) => cellText(row.teacher_name || "—"),
    },

    // Term (CENTER + muted)
    {
      key: "term",
      field: "term",
      label: "Term",
      minWidth: 120,
      width: "120px",
      align: "center",
      headerAlign: "center" as any,
      customClass: "col-muted",
      render: (row) => cellText(row.term ?? "—", true),
    },

    // Created at (CENTER + muted + responsive hide)
    {
      key: "created_at",
      field: "created_at" as any,
      label: "Created",
      minWidth: 180,
      customClass: "col-hide-md col-muted",
      align: "center",
      headerAlign: "center" as any,
      render: (row) =>
        mutedWrap(h(DateTimeCell, { value: getLifecycleCreatedAt(row) })),
    },

    // Actions (CENTER)
    {
      label: "Actions",
      slotName: "operation",
      operation: true,
      fixed: "right",
      width: "220px",
      align: "center",
      headerAlign: "center" as any,
    },
  ];
}
