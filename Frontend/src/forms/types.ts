import type { Field } from "~/components/types/form";
import type { formRegistryCreate, formRegistryEdit } from "./admin/register";

/* -------------------------------
 * Generic Form Service
 * ------------------------------- */
export interface UseFormService<
  TCreate,
  TUpdate,
  TDelete = boolean,
  TRetrieve = any
> {
  create?: (data: TCreate) => Promise<TRetrieve>;
  update: (id: string, data: TUpdate) => Promise<TRetrieve>;
  delete?: (id: string) => Promise<TDelete>;
  getDetail?: (id: string) => Promise<TRetrieve>;
}

/* -------------------------------
 * Form Modes & Entities
 * ------------------------------- */
export type FormMode = "CREATE" | "EDIT";
export type FormEntity = "USER" | "STAFF" | "STUDENT" | "CLASS" | "SUBJECT";

/* -------------------------------
 * Dynamic Form Registry Item
 * ------------------------------- */
export interface DynamicFormRegistryItem<TCreate, TUpdate> {
  service: () => UseFormService<TCreate, TUpdate>;
  schema: Field<TCreate | TUpdate>[];
  formData: () => TCreate | TUpdate;
}

/* -------------------------------
 * Dynamic Form Registry Map
 * ------------------------------- */
export type DynamicFormRegistry = Record<
  FormEntity,
  DynamicFormRegistryItem<any, any>
>;

/* -------------------------------
 * Infer Create Form Item
 * ------------------------------- */
export type CreateFormItem<T extends keyof typeof formRegistryCreate> =
  (typeof formRegistryCreate)[T] extends {
    service: () => UseFormService<infer C, infer U>;
    formData: () => infer F;
    schema: Field<infer SchemaType>[];
  }
    ? {
        service: UseFormService<C, U>;
        formData: F;
        schema: Field<SchemaType>[];
      }
    : never;

/* -------------------------------
 * Infer Edit Form Item
 * ------------------------------- */
export type EditFormItem<T extends keyof typeof formRegistryEdit> =
  (typeof formRegistryEdit)[T] extends {
    service: () => UseFormService<infer C, infer U>;
    formData: () => infer F;
    schema: Field<infer SchemaType>[];
  }
    ? {
        service: UseFormService<C, U>;
        formData: F;
        schema: Field<SchemaType>[];
      }
    : never;
