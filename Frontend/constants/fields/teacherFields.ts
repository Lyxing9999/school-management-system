import type { Field } from "./types/Field";

export const teacherFields: Field[] = [
  /**
   * Field schema for teacher information form/table
   *
   * Properties:
   * label       - Display label for the field
   * key         - Unique key to identify the field (supports dot notation for nested fields)
   * children    - Optional array of sub-fields for nested/grouped data
   * showSaveCancelControls - show inline edit save/cancel buttons for this field (default: TRUE)
   * format      - Optional string to specify formatting (e.g., date format)
   * type        - Input type from InputTypeEnum ("string", "number", "date", etc.)
   * isArray     - Boolean indicating if the field holds an array of values
   * isDate      - Boolean indicating if the field represents a date (used for formatting/UI)
   * isDict      - Boolean indicating if the field holds a dictionary/object
   * readonly    - If true, field is read-only
   * disabled    - If true, field is disabled (not editable) in the UI
   *
   * Future planned features:
   * pass
   */

  { label: "Phone Number", key: "phone_number", type: "string" },
  {
    label: "Teacher Info",
    key: "teacher_info",
    children: [
      { label: "Lecturer ID", key: "teacher_info.lecturer_id", type: "string" },
      {
        label: "Lecturer Name",
        key: "teacher_info.lecturer_name",
        type: "string",
      },
      {
        label: "Subjects",
        key: "teacher_info.subjects",
        isArray: true,
        type: "string",
      },
      {
        label: "Created At",
        key: "teacher_info.created_at",
        isDate: true,
        type: "date",
        readonly: true,
        disabled: true,
        format: "YYYY-MM-DD",
        showInputField: true,
      },
      {
        label: "Updated At",
        key: "teacher_info.updated_at",
        isDate: true,
        type: "date",
        readonly: true,
        disabled: true,
        format: "YYYY-MM-DD",
        showInputField: true,
      },
    ],
  },
];
