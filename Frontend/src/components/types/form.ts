import type { Component, Ref } from "vue";

export type Field<T = any> = {
  // The property key in the model
  key?: keyof T;

  // Display label
  label?: string;

  // Width and position for the label
  labelWidth?: string;
  labelPosition?: "top" | "left";

  displayOnly?: boolean;

  rules?: any[];

  component?: Component;

  // Props to pass to the component
  componentProps?: Record<string, unknown>;

  // Optional child component (like ElOption) and props (for select/dropdown)
  childComponent?: Component;
  childComponentProps?: {
    options?: { [key: string]: any }[] | Ref<{ [key: string]: any }[]>;
    valueKey?: string;
    labelKey?: string;
  };

  iconComponent?: Component;
  iconComponentProps?: Record<string, unknown>;

  type?: "tags";

  row?: Field<T>[];
};
