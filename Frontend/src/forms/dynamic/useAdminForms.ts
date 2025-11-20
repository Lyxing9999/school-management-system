import { computed, unref, type Ref } from "vue";
import { useFormCreate } from "~/composables/useFormCreate";
import { useFormEdit } from "~/composables/useFormEdit";
import { formRegistryCreate, formRegistryEdit } from "~/forms/admin/register";
import type {
  ServiceOfCreate,
  FormDataOfCreate,
  SchemaOfCreate,
  ServiceOfEdit,
  FormDataOfEdit,
  SchemaOfEdit,
} from "~/forms/types/dynamicFormTypes";
import type { UseFormService } from "~/forms/types";
import { toInlineEditUpdateService } from "~/composables/inline-edit/useInlineEdit";
import type { UseInlineEditService } from "~/composables/inline-edit/useInlineEdit";

/** -------------------------------
 * Dynamic Create Form Hook
 * ------------------------------- */
export function useDynamicCreateFormReactive<
  T extends keyof typeof formRegistryCreate
>(mode: Ref<T>) {
  const registry = computed(() => {
    const item = formRegistryCreate[unref(mode)];
    if (!item) {
      throw new Error(`Create form for ${unref(mode)} is not defined`);
    }
    return item;
  });

  type FormData = NonNullable<FormDataOfCreate<T>>;
  type Schema = SchemaOfCreate<T>;
  type Service = ServiceOfCreate<T> extends () => infer S ? S : never;

  return useFormCreate<FormData, FormData>(
    () =>
      registry.value.service() as Service & UseFormService<FormData, FormData>,
    () => registry.value.formData?.() ?? ({} as FormData),
    () => registry.value.schema as Schema
  );
}

/** -------------------------------
 * Dynamic Edit Form Hook
 * ------------------------------- */
export function useDynamicEditFormReactive<
  T extends keyof typeof formRegistryEdit
>(mode: Ref<T>) {
  const registry = computed(() => {
    const item = formRegistryEdit[unref(mode)];
    if (!item) {
      throw new Error(`Edit form for ${unref(mode)} is not defined`);
    }
    return item;
  });

  type FormData = NonNullable<FormDataOfEdit<T>>;
  type Schema = SchemaOfEdit<T>;
  type Service = ServiceOfEdit<T> extends () => infer S ? S : never;

  return useFormEdit<FormData, FormData>(
    () =>
      registry.value.service() as Service & UseFormService<FormData, FormData>,
    () => registry.value.formData?.() ?? ({} as FormData),
    () => registry.value.schema as Schema
  );
}

/** -------------------------------
 * inline Edit Form Hook
 * ------------------------------- */

export function useInlineEditService<T extends keyof typeof formRegistryEdit>(
  mode: T
): ComputedRef<UseInlineEditService<NonNullable<FormDataOfEdit<T>>>> {
  const registryItem = formRegistryEdit[mode];

  if (!registryItem) {
    throw new Error(`Edit form for ${mode} is not defined`);
  }

  type FormData = NonNullable<FormDataOfEdit<T>>;

  const service = () =>
    registryItem.service() as UseFormService<any, Partial<FormData>>;

  return computed(() => toInlineEditUpdateService<FormData>(service));
}
