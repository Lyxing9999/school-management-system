import type { VNode, Component } from "vue";
export type RenderConfig = {
  component?: Component;
  componentProps?: Record<string, any>;
  value?: any;
};
export type CellRenderValue = VNode | string | RenderConfig;
/**
 * slots map
 */

export type ChildComponentSlots = {
  append?: () => VNode | VNode[] | null;
  prefix?: () => VNode | VNode[] | null;
  footer?: () => VNode | VNode[] | null;
};

/**
 * Inline edit props MultiTypeEditCell
 * @template R - The type of the row data
 * @template F - The type of the field
 */
export type InlineEditProps<
  R extends Record<string, any>,
  F extends keyof R
> = {
  row: R;
  field: F;
  modelValue: R[F];
  rules?: Rule[];
  component?: Component;
  componentProps?: Record<string, unknown>;
  childComponent?: Component;
  childComponentProps?: {
    options?: Array<Record<string, any>>;
    valueKey?: string;
    labelKey?: string;
    appendValue?: string;
    prependValue?: string;
    slots?: ChildComponentSlots;
  };
  slotName?: string;
  inlineEditActive?: boolean;
  controls?: boolean;
  revertSlots?: boolean;
  autoSave?: boolean;
  debounceMs?: number;
  customClass?: string;
  loading?: boolean;
};

/**
 * Inline edit column props EditableColumn
 * @template R - The type of the row data
 * @template F - The type of the field
 */
export type InlineEditColumnProps<
  R extends Record<string, any>,
  F extends keyof R
> = {
  field: F;
  label?: string;
  component?: Component;
  componentProps?: Record<string, unknown>;
  rules?: Rule[];
  childComponent?: Component;
  childComponentProps?: {
    options?: Array<Record<string, any>>;
    valueKey?: string;
    labelKey?: string;
    appendValue?: string;
    prependValue?: string;
    slots?: ChildComponentSlots;
  };
  inlineEditActive?: boolean;
  placeholder?: string;
  controls?: boolean;
  revertSlots?: boolean;
  autoSave?: boolean;
  align?: "left" | "center" | "right";
  render?: (row: R, field: F) => CellRenderValue;
  debounceMs?: number;
  operation?: boolean;
  customClass?: string;
  footer?: boolean;
  slotName?: string;
  useSlot?: boolean;
};

/**
 * Column config SmartTable
 * @template T - The type of the row data
 */
export type ColumnConfig<T> = {
  label: string;
  field?: keyof T;
  inlineEditActive?: boolean;
  autoSave?: boolean;
  render?: (row: T, field: keyof T) => CellRenderValue;
  align?: "left" | "center" | "right" | undefined;
  placeholder?: string;
  clearable?: boolean;
  controls?: boolean;
  revertSlots?: boolean;
  operation?: boolean;
  debounceMs?: number;
  component?: Component;
  componentProps?: Record<string, unknown>;
  childComponent?: Component;
  rules?: Rule[];
  footer?: boolean;
  slotName?: string;
  useSlot?: boolean;
  childComponentProps?: {
    options?: Array<Record<string, any>>;
    valueKey?: string;
    labelKey?: string;
    appendValue?: string;
    prependValue?: string;
    slots?: ChildComponentSlots;
  };
  customClass?: string;
  // el-table-column props
  fixed?: "left" | "right";
  width?: string;
  [key: string]: unknown;
};

export type Rule = {
  required?: boolean;
  min?: number;
  max?: number;
  pattern?: RegExp;
  message: string;
  trigger?: "blur" | "change";
  validator?: (
    rule: Rule,
    value: any,
    callback: (error?: Error) => void
  ) => void;
};
