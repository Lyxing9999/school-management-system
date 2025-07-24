import type { Field } from "./types/Field";

export const studentFields: Field[] = [
  /**
   * Field schema for student information form/table
   *
   * Properties:
   * label       - Display label for the field
   * key         - Unique key for the field (supports nested keys via dot notation)
   * children    - Optional nested fields group
   *
   * format      - Optional formatting string (e.g. for dates)
   * type        - Input type from InputTypeEnum ("string", "number", "date", "email", etc.)
   * isArray     - True if field stores multiple values (array)
   * isDate      - True if field represents a date (for UI formatting)
   * isDict      - True if field stores a dictionary/object
   * readonly    - True if field is read-only
   * disabled    - True if field is disabled in UI (not editable)
   * showInputField - True if field should show input field
   *
   * * Future planned features:
   * pass
   */
  {
    label: "Student ID",
    key: "student_info.student_id",
    type: "string",
    showSaveCancelControls: false,
  },
  { label: "Grade", key: "student_info.grade", type: "number" },
  {
    label: "Class IDs",
    key: "student_info.class_ids",
    isArray: true,
    type: "string",
  },
  { label: "Major", key: "student_info.major", type: "string" },
  {
    label: "Birth Date",
    key: "student_info.birth_date",
    isDate: true,
    type: "date",
    format: "YYYY-MM-DD",
  },
  { label: "Batch", key: "student_info.batch", type: "string" },
  { label: "Address", key: "student_info.address", type: "string" },
  { label: "Phone Number", key: "student_info.phone_number", type: "string" },
  { label: "Email", key: "student_info.email", type: "email" },
  {
    label: "Attendance Record",
    key: "student_info.attendance_record",
    isDict: true,
    type: "dict",
  },
  {
    label: "Courses Enrolled",
    key: "student_info.courses_enrolled",
    isArray: true,
    type: "string",
  },
  {
    label: "Scholarships",
    key: "student_info.scholarships",
    isArray: true,
    type: "string",
  },
  { label: "Current GPA", key: "student_info.current_gpa", type: "float" },
  {
    label: "Remaining Credits",
    key: "student_info.remaining_credits",
    type: "float",
  },
  {
    label: "Created At",
    key: "student_info.created_at",
    isDate: true,
    type: "date",
    readonly: true,
    disabled: true,
    format: "YYYY-MM-DD",
    showInputField: true,
  },
  {
    label: "Updated At",
    key: "student_info.updated_at",
    isDate: true,
    type: "date",
    readonly: true,
    disabled: true,
    format: "YYYY-MM-DD",
    showInputField: true,
  },
];
