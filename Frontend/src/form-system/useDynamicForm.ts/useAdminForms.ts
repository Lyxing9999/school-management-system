import { computed, unref, type Ref, type ComputedRef } from "vue";

import { useFormCreate } from "~/composables/useFormCreate";
import { useFormEdit } from "~/composables/useFormEdit";
import {
  toInlineEditUpdateService,
  type UseInlineEditService,
} from "~/composables/useInlineEdit";

import {
  adminFormRegistryCreate,
  adminFormRegistryEdit,
} from "~/form-system/register/admin";

import type {
  CreateFormItem,
  EditFormItem,
} from "~/form-system/types/dynamicFormTypes";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";

/** -------------------------------
 * Dynamic Create Form Hook
 * ------------------------------- */
export function useDynamicCreateFormReactive<
  T extends keyof typeof adminFormRegistryCreate
>(mode: Ref<T>) {
  const registry = computed(() => {
    const key = unref(mode);
    const item = adminFormRegistryCreate[key];

    if (!item) {
      throw new Error(`Create form for ${String(key)} is not defined`);
    }
    return item;
  });

  type Item = CreateFormItem<typeof adminFormRegistryCreate, T>;
  // Ensure we satisfy useFormCreate's Record<string, any> constraint
  type FormData = Item["formData"] & Record<string, any>;
  type Schema = Item["schema"];

  return useFormCreate<FormData, FormData>(
    () =>
      // We only need the create path; extra fields (update/delete) are ignored.
      registry.value.service() as unknown as UseFormService<
        FormData,
        any,
        any,
        FormData,
        FormData,
        FormData
      >,
    () => (registry.value.formData?.() ?? {}) as FormData,
    () => registry.value.schema as Schema
  );
}

/** -------------------------------
 * Dynamic Edit Form Hook
 * ------------------------------- */
export function useDynamicEditFormReactive<
  T extends keyof typeof adminFormRegistryEdit
>(mode: Ref<T>) {
  const registry = computed(() => {
    const key = unref(mode);
    const item = adminFormRegistryEdit[key];

    if (!item) {
      throw new Error(`Edit form for ${String(key)} is not defined`);
    }
    return item;
  });

  type Item = EditFormItem<typeof adminFormRegistryEdit, T>;
  // Update DTO, forced to satisfy Record<string, any>
  type FormData = Item["formData"] & Record<string, any>;
  type Schema = Item["schema"];

  return useFormEdit<FormData, FormData>(
    () =>
      // useFormEdit expects UseFormService<undefined, FormData, undefined, FormData, FormData, FormData>
      // We adapt/cast our concrete service to that shape, ignoring delete/create.
      registry.value.service() as unknown as UseFormService<
        undefined,
        FormData,
        undefined,
        FormData,
        FormData,
        FormData
      >,
    () => registry.value.formData?.() ?? ({} as FormData),
    () => registry.value.schema as Schema
  );
}

/** -------------------------------
 * Inline Edit Form Hook
 * ------------------------------- */
export function useInlineEditService<
  T extends keyof typeof adminFormRegistryEdit
>(
  mode: T
): ComputedRef<
  UseInlineEditService<
    EditFormItem<typeof adminFormRegistryEdit, T>["formData"] &
      Record<string, any>
  >
> {
  const registryItem = adminFormRegistryEdit[mode];

  if (!registryItem) {
    throw new Error(`Edit form for ${String(mode)} is not defined`);
  }

  type Item = EditFormItem<typeof adminFormRegistryEdit, T>;
  type FormData = Item["formData"] & Record<string, any>;

  const service = () =>
    // Inline edit uses only update; we allow partial updates here.
    registryItem.service() as unknown as UseFormService<any, Partial<FormData>>;

  return computed(() => toInlineEditUpdateService<FormData>(service));
}
