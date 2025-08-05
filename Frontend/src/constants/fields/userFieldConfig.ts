import type { ColumnConfig } from "~/constants/fields/types/FieldConfig";
import type { User } from "~/types/models/User";
import { renderUserRole } from "~/constants/renders/roleTag";

export const userFieldsSchema: ColumnConfig<User>[] = [
  /**
   * Key: required field key in the model
   * label: displayed column header in the UI
   * type: input type (e.g., string, email, date, operation, etc.)
   *
   * Optional:
   * readonly - if true, field cannot be edited by the user
   * disabled - if true, field is disabled in the UI (not interactive)
   * showSaveCancelControls - show inline edit save/cancel buttons for this field
   * slot - use a custom UI slot/component for rendering this field
   * render - function to customize rendering of field content
   *
   * Future extensions (planned enhancements):
   * pass
   */

  {
    field: "username",
    label: "Username",
    type: "string",
  },
  {
    field: "email",
    label: "Email",
    type: "email",
  },
  {
    field: "role",
    label: "Role",
    type: "string",
    readonly: true,
    showSaveCancelControls: false,
    render: (row) => renderUserRole(row),
  },
  {
    field: "createdAt",
    label: "Created At",
    type: "date",
    disabled: true,
    readonly: true,
    showInputField: true,
  },
  {
    field: "updatedAt",
    label: "Updated At",
    type: "date",
    disabled: true,
    readonly: true,
    showInputField: true,
  },
  {
    field: "actions" as keyof User,
    label: "Actions",
    type: "operation",
    slot: true,
  },
];
