import type { InputType } from "~/constants/fields/types/Field";

export interface ColumnConfig<T> {
  field: keyof T;
  label: string;
  type: InputType;
  disabled?: boolean;
  readonly?: boolean;
  showSaveCancelControls?: boolean;
  slot?: boolean;
  showInputField?: boolean;
  render?: (row: T) => any;
}
