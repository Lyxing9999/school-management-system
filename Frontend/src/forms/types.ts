import type { Field } from "~/components/types/form";
import type { formRegistryCreate, formRegistryEdit } from "./admin/register";

/** -------------------------------
 * Generic Form Service
 * ------------------------------- */
export interface UseFormService<C, U, D = boolean, R = any> {
  create?: (data: C) => Promise<R>;
  update: (id: string, data: U) => Promise<R>;
  delete?: (id: string) => Promise<D>;
  getDetail?: (id: string) => Promise<R>;
}

/** -------------------------------
 * Form Modes & Entities
 * ------------------------------- */
export type FormMode = "CREATE" | "EDIT";
export type FormEntity = "USER" | "STAFF" | "STUDENT" | "CLASS" | "SUBJECT";

/** -------------------------------
 * Dynamic Form Registry Item
 * ------------------------------- */
export interface DynamicFormRegistryItem<C, U> {
  service: {
    create?: (data: C) => Promise<any>;
    update?: (id: string, data: U) => Promise<any>;
  };
  schema: Field<C | U>[];
  formData: () => C | U;
}

/** -------------------------------
 * Dynamic Form Registry Map
 * ------------------------------- */
export type DynamicFormRegistry = Record<
  FormEntity,
  DynamicFormRegistryItem<any, any>
>;

export type CreateFormItem<T extends keyof typeof formRegistryCreate> =
  (typeof formRegistryCreate)[T] extends {
    service: () => infer S;
    formData: () => infer F;
    schema: Field<infer FSchema>[];
  }
    ? { service: S; formData: F; schema: Field<F>[] }
    : never;

/** -------------------------------
 * Infer Edit Form Type
 * ------------------------------- */
export type EditFormItem<T extends keyof typeof formRegistryEdit> =
  (typeof formRegistryEdit)[T] extends {
    service: () => infer S;
    formData: () => infer F;
    schema: Field<infer FSchema>[];
  }
    ? { service: S; formData: F; schema: Field<F>[] }
    : never;
