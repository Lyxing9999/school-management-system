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
  controlsSlot?: boolean;
  autoSave?: boolean;
  debounceMs?: number;
  customClass?: string;
};

import type { VNode, Component } from "vue";

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
  controlsSlot?: boolean;
  autoSave?: boolean;
  align?: "left" | "center" | "right";
  render?: (row: R, field: F) => VNode;
  debounceMs?: number;
  operation?: boolean;
  customClass?: string;
  footer?: boolean;
  slotName?: string;
  useSlots?: boolean;
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
  render?: (row: T, field: keyof T) => VNode;
  align?: "left" | "center" | "right" | undefined;
  placeholder?: string;
  clearable?: boolean;
  controls?: boolean;
  controlsSlot?: boolean;
  operation?: boolean;
  debounceMs?: number;
  component?: Component;
  componentProps?: Record<string, unknown>;
  childComponent?: Component;
  rules?: Rule[];
  footer?: boolean;
  slotName?: string;
  useSlots?: boolean;
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
