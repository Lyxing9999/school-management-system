export type Field = {
  key: string;
  label: string;
  labelWidth?: string;
  labelPosition?: "top" | "left";
  displayOnly?: boolean;
  rules?: any[];
  component?: Component;
  componentProps?: Record<string, unknown>;
  childComponent?: Component;
  iconComponent?: Component;
  iconComponentProps?: Record<string, unknown>;
  childComponentProps?: {
    options?: { [key: string]: any }[];
    valueKey?: string;
    labelKey?: string;
  };
};
