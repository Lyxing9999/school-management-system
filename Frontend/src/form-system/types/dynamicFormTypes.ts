import type { Field } from "~/components/types/form";

/**
 * Generic type to extract the “create form item”
 * from any registry object whose values look like:
 * { service: () => S; formData: () => F; schema: Field<FS>[] }
 */
export type CreateFormItem<
  TRegistry,
  TKey extends keyof TRegistry
> = TRegistry[TKey] extends {
  service: () => infer S;
  formData: () => infer F;
  schema: Field<infer FS>[];
}
  ? {
      service: S;
      formData: F;
      schema: Field<FS>[];
    }
  : never;

/**
 * Generic type to extract the “edit form item”
 * from any registry object whose values look like:
 * { service: () => S; formData: () => F; schema: Field<FS>[] }
 */
export type EditFormItem<
  TRegistry,
  TKey extends keyof TRegistry
> = TRegistry[TKey] extends {
  service: () => infer S;
  formData: () => infer F;
  schema: Field<infer FS>[];
}
  ? {
      service: S;
      formData: F;
      schema: Field<FS>[];
    }
  : never;

/** Extract just the service type from a registry + key */
export type ServiceOfCreate<
  TRegistry,
  TKey extends keyof TRegistry
> = CreateFormItem<TRegistry, TKey>["service"];

export type ServiceOfEdit<
  TRegistry,
  TKey extends keyof TRegistry
> = EditFormItem<TRegistry, TKey>["service"];

/** Extract just the formData type from a registry + key */
export type FormDataOfCreate<
  TRegistry,
  TKey extends keyof TRegistry
> = CreateFormItem<TRegistry, TKey>["formData"];

export type FormDataOfEdit<
  TRegistry,
  TKey extends keyof TRegistry
> = EditFormItem<TRegistry, TKey>["formData"];

/** Extract just the schema type from a registry + key */
export type SchemaOfCreate<
  TRegistry,
  TKey extends keyof TRegistry
> = CreateFormItem<TRegistry, TKey>["schema"];

export type SchemaOfEdit<
  TRegistry,
  TKey extends keyof TRegistry
> = EditFormItem<TRegistry, TKey>["schema"];
