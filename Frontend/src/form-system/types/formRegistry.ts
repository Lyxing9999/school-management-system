// src/form-system/types/formRegistry.ts (adjust path to yours)
import type { Field } from "~/components/types/form";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";

/**
 * Registry item for CREATE flows.
 *
 * C = create/form DTO
 * U = update DTO used by the same service
 */
export type FormRegistryCreateItem<C, U = unknown> = {
  service: () => UseFormService<C, U>;
  schema: Field<C>[];
  formData: () => C;
};

/**
 * Registry item for EDIT flows.
 *
 * C is usually the create DTO (or never if unused),
 * U is the update DTO.
 */
export type FormRegistryEditItem<C, U> = {
  service: () => UseFormService<C, U>;
  schema: Field<Partial<U>>[];
  formData: () => U;
};
