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
    slots?: {
      append?: () => VNode;
      prefix?: () => VNode;
    };
  };
  inlineEditActive?: boolean;
  controls?: boolean;
  controlsSlot?: boolean;
  autoSave?: boolean;
  debounceMs?: number;
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
    slots?: {
      append?: () => VNode;
      prefix?: () => VNode;
    };
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
};

/**
 * Column config SmartTable
 * @template T - The type of the row data
 */
export type ColumnConfig<T> = {
  label: string;
  field: keyof T;
  inlineEditActive?: boolean;
  autoSave?: boolean;
  render?: (row: T, field: keyof T) => VNode;
  align?: "left" | "center" | "right" | undefined;
  placeholder?: string;
  clearable?: boolean;
  controls?: boolean;
  controlsSlot?: boolean;
  debounceMs?: number;
  component?: Component;
  componentProps?: Record<string, unknown>;
  operation?: boolean;
  childComponent?: Component;
  rules?: Rule[];
  childComponentProps?: {
    options?: Array<Record<string, any>>;
    valueKey?: string;
    labelKey?: string;
    appendValue?: string;
    prependValue?: string;
    slots?: {
      append?: () => VNode;
      prefix?: () => VNode;
    };
  };

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
