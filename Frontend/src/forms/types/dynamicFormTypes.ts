import type { Field } from "~/components/types/form";
import type { formRegistryCreate, formRegistryEdit } from "../admin/register";
import type { UseFormService } from "../types";

/** -------------------------------
 * Extract Create Form Item
 * ------------------------------- */
export type CreateFormItem<T extends keyof typeof formRegistryCreate> =
  (typeof formRegistryCreate)[T] extends {
    service: () => infer S;
    formData: () => infer F;
    schema: Field<infer FS>[];
  }
    ? {
        service: S; // UseFormService<C, U>
        formData: F; // Create DTO
        schema: Field<FS>[]; // Schema fields
      }
    : never;

/** -------------------------------
 * Extract Edit Form Item
 * ------------------------------- */
export type EditFormItem<T extends keyof typeof formRegistryEdit> =
  (typeof formRegistryEdit)[T] extends {
    service: () => infer S;
    formData: () => infer F;
    schema: Field<infer FS>[];
  }
    ? {
        service: S; // UseFormService<C, U>
        formData: F; // Edit DTO
        schema: Field<FS>[]; // Schema fields
      }
    : never;

/** -------------------------------
 * Extract just Service type
 * ------------------------------- */
export type ServiceOfCreate<T extends keyof typeof formRegistryCreate> =
  CreateFormItem<T>["service"];

export type ServiceOfEdit<T extends keyof typeof formRegistryEdit> =
  EditFormItem<T>["service"];

/** -------------------------------
 * Extract just FormData type
 * ------------------------------- */
export type FormDataOfCreate<T extends keyof typeof formRegistryCreate> =
  CreateFormItem<T>["formData"];

export type FormDataOfEdit<T extends keyof typeof formRegistryEdit> =
  EditFormItem<T>["formData"];

/** -------------------------------
 * Extract just Schema type
 * ------------------------------- */
export type SchemaOfCreate<T extends keyof typeof formRegistryCreate> =
  CreateFormItem<T>["schema"];

export type SchemaOfEdit<T extends keyof typeof formRegistryEdit> =
  EditFormItem<T>["schema"];
