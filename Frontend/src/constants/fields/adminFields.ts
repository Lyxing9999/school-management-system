import type { Field } from "./types/Field";

export const adminFields: Field[] = [
  { label: "Phone Number", key: "admin_info.phone_number", type: "string" },
  { label: "Admin ID", key: "admin_info.admin_id", type: "string" },
  {
    label: "Created At",
    key: "admin_info.created_at",
    isDate: true,
    type: "date",
  },
  {
    label: "Updated At",
    key: "admin_info.updated_at",
    isDate: true,
    type: "date",
  },
];
