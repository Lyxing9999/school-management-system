import type { Component, Ref, UnwrapRef } from "vue";
import type { FormItemProps } from "element-plus";

export type Field<T = Record<string, any>> = {
  key?: Extract<keyof T, string>; // property key in form object
  label?: string;
  displayOnly?: boolean;
  formItemProps?: Partial<FormItemProps>;
  component?: Component;
  componentProps?: Record<string, unknown>;
  childComponent?: Component;
  childComponentProps?: {
    options?:
      | { value: any; label: string }[]
      | Ref<{ value: any; label: string }[]> // reactive options
      | (() => { value: any; label: string }[]);
    valueKey?: string;
    labelKey?: string;
  };
  iconComponent?: Component;
  iconComponentProps?: Record<string, unknown>;
  type?: "tags";
  row?: Field<T>[]; // support nested row fields
};
