import { computed, unref, type Ref } from "vue";

import type { UseFormService } from "~/services/types";

import { useFormCreate } from "~/composables/useFormCreate";
import { useFormEdit } from "~/composables/useFormEdit";
import type {
  EditRegistryItem,
  CreateFormMap,
  GetFormMap,
  RoleEditMap,
  FormRegistryCreateItem,
  FormRegistryEditItem,
} from "~/schemas/types/admin";
import type { Field } from "~/components/types/form";
import {
  toInlineEditUpdateService,
  type UseInlineEditService,
} from "~/composables/inline-edit/useInlineEdit";

import { formRegistryCreate, formRegistryEdit } from "./AdminFormRegistry";

export function useDynamicCreateFormReactive<T extends keyof CreateFormMap>(
  mode: Ref<T>
) {
  const registry = computed(
    () =>
      formRegistryCreate[unref(mode)] as FormRegistryCreateItem<
        CreateFormMap[T]
      >
  );

  return useFormCreate<CreateFormMap[T], GetFormMap[T]>(
    () => registry.value.service,
    () =>
      registry.value.formData
        ? registry.value.formData()
        : ({} as CreateFormMap[T]),
    () => registry.value.schema as Field<CreateFormMap[T]>[]
  );
}

export function useDynamicEditFormReactive<T extends keyof EditRegistryItem>(
  mode: Ref<T>
) {
  const registry = computed(
    () => formRegistryEdit[unref(mode)] as FormRegistryEditItem<RoleEditMap[T]>
  );

  return useFormEdit<RoleEditMap[T], RoleEditMap[T]>(
    () => registry.value.service,
    () =>
      registry.value.formData
        ? registry.value.formData()
        : ({} as RoleEditMap[T]),
    () => registry.value.schema as Field<RoleEditMap[T]>[]
  );
}

export function useInlineEditService<K extends keyof EditRegistryItem>(key: K) {
  const registryItem = formRegistryEdit[key];

  type TGet = ReturnType<NonNullable<typeof registryItem.formData>>;
  type TUpdate = RoleEditMap[K];

  const service = registryItem.service as UseFormService<
    any,
    Partial<TUpdate>,
    TGet,
    TGet,
    never
  >;

  return computed(() =>
    toInlineEditUpdateService<TUpdate>(service)
  ) as ComputedRef<UseInlineEditService<TUpdate>>;
}
