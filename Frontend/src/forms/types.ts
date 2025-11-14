import type { Field } from "~/components/types/form";

export interface UseFormService<
  C, // Create type
  U, // Update type
  D = boolean, // Delete return type
  R = any // Detail type
> {
  create?: (data: C) => Promise<R>;
  update: (id: string, data: U) => Promise<R>;
  delete?: (id: string) => Promise<D>;
  getDetail?: (id: string) => Promise<R>;
}

export type FormMode = "CREATE" | "EDIT";
export type FormEntity = "USER" | "STAFF" | "STUDENT" | "CLASS" | "SUBJECT";

export interface DynamicFormRegistryItem<C, U> {
  service: {
    create?: (data: C) => Promise<any>;
    update?: (id: string, data: U) => Promise<any>;
  };
  schema: Field[];
  formData: () => C | U;
}

export type DynamicFormRegistry = Record<
  FormEntity,
  DynamicFormRegistryItem<any, any>
>;
