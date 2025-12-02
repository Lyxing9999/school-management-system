import {
  ref,
  computed,
  unref,
  watch,
  toRaw,
  nextTick,
  type Ref,
  type ComputedRef,
} from "vue";
import type { UseFormService } from "~/forms/types/serviceFormTypes";
import type { Field } from "~/components/types/form";

import { useMessage } from "~/composables/common/useMessage";

export type InitialData<I> =
  | Partial<I>
  | Ref<Partial<I>>
  | ComputedRef<Partial<I>>;

type WithResult<T> = { result: T };

/**
 * useFormEdit
 * Handles dynamic edit/detail forms with PATCH / PUT support.
 * - PATCH: send only changed fields
 * - PUT:   send full filtered data
 */
export function useFormEdit<I extends object, O extends I = I>(
  getService: () => UseFormService<undefined, I, undefined, O>,
  getDefaultData: () => I,
  getFields: () => Field<I>[]
) {
  const service = computed(() => getService());
  const formDialogVisible = ref(false);
  const loading = ref(false);
  const saveId = ref<string | number>("");

  // current form state (what user edits)
  const formData = ref<Partial<I>>({});

  // original data loaded from API for this record
  const reactiveInitialData = ref<Partial<I>>({});

  // diff vs initial (for PATCH)
  const patchData = ref<Partial<I>>({});

  const schema = computed(() => unref(getFields()));
  const defaultData = computed(() => unref(getDefaultData()));

  /**
   * Track diffs:
   * whenever formData changes, compute patchData compared to reactiveInitialData
   */
  watch(
    formData,
    (newVal) => {
      if (!newVal || typeof newVal !== "object") return;

      const fields = schema.value;
      const nextDiff: Partial<I> = {};

      const collectDiffs = (fields: Field<I>[]) => {
        fields.forEach((field) => {
          const rowFields = field.row ?? [field];

          rowFields.forEach((f) => {
            const key = f.key as keyof I | undefined;
            if (!key) return;

            const newValue = (newVal as any)[key];
            const oldValue = (reactiveInitialData.value as any)[key];

            if (newValue !== oldValue) {
              (nextDiff as any)[key] = newValue;
            }
          });
        });
      };

      collectDiffs(fields);
      patchData.value = nextDiff;
    },
    { deep: true }
  );

  /**
   * Reset form data (defaults to reactiveInitialData)
   */
  const resetFormData = (data?: Partial<I>) => {
    const safeInitial = reactiveInitialData.value || {};
    formData.value = { ...safeInitial, ...data } as Partial<I>;
  };

  /**
   * Open form and load detail by ID
   */
  const openForm = async (id: string | number) => {
    if (!service.value?.getDetail) return;
    loading.value = true;
    saveId.value = id;

    reactiveInitialData.value = {};
    formData.value = {};
    patchData.value = {};

    try {
      const detail = await service.value.getDetail(saveId.value.toString());
      const data = (
        detail && "result" in detail ? (detail as WithResult<O>).result : detail
      ) as Partial<I> | null | undefined;

      if (!data || Object.keys(data).length === 0) {
        reactiveInitialData.value = { ...defaultData.value };
        resetFormData(defaultData.value);
      } else {
        reactiveInitialData.value = toRaw(data);
        resetFormData(data);
      }

      // clear diffs for this record
      patchData.value = {};

      // open after data is ready
      formDialogVisible.value = true;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Save form
   * - PATCH: send only changed fields (patchData)
   * - PUT:   send full filteredData
   */
  const saveForm = async (
    payload: Partial<I>,
    method: "PATCH" | "PUT" = "PATCH"
  ): Promise<boolean> => {
    if (!service.value.update) return false;
    loading.value = true;

    try {
      // Merge external payload (from SmartForm) into formData
      if (payload && Object.keys(payload).length > 0) {
        Object.assign(formData.value, payload);
        await nextTick();
      }

      const fields = schema.value as Field<I>[];
      const filteredData: Partial<I> = {};

      // Collect only keys defined in the form schema from formData
      const collectKeys = (fields: Field<I>[]) => {
        fields.forEach((field) => {
          if (field.row) {
            collectKeys(field.row);
          } else if (field.key != null && field.key in formData.value) {
            filteredData[field.key] = formData.value[field.key];
          }
        });
      };

      collectKeys(fields);

      // Handle file upload into filteredData
      if (
        "photo_file" in formData.value &&
        (formData.value as any).photo_file
      ) {
        const file = (formData.value as any).photo_file as File;
        (filteredData as any).photo_file = file;
      }

      // Decide what to send
      let basePayload: Partial<I>;

      if (method === "PATCH") {
        const hasDiff = Object.keys(patchData.value).length > 0;

        if (!hasDiff) {
          useMessage().showInfo("No changes detected, skip update");
          return true;
        }

        // Only changed fields
        basePayload = patchData.value;
      } else {
        // PUT: full object
        basePayload = filteredData as I;
      }

      // If you need FormData (for file upload), convert here; otherwise send as JSON
      let body: any = basePayload;
      if ((basePayload as any).photo_file instanceof File) {
        const fd = new FormData();
        Object.entries(basePayload as Record<string, any>).forEach(
          ([key, value]) => {
            if (value !== undefined && value !== null) {
              fd.append(key, value);
            }
          }
        );
        body = fd;
      }

      let response: I | null = null;

      try {
        response = await service.value.update(saveId.value.toString(), body);
      } catch (err: any) {
        return false;
      }

      if (response) {
        // Refresh initial data with response, reset form, close dialog
        reactiveInitialData.value = toRaw(response);
        resetFormData(response);
        patchData.value = {};
        formDialogVisible.value = false;
        return true;
      }

      return false;
    } finally {
      loading.value = false;
    }
  };

  /**
   * Cancel: discard edits and close dialog
   */
  const cancelForm = () => {
    // Restore form to initial data and clear diffs
    resetFormData();
    patchData.value = {};
    formDialogVisible.value = false;
  };

  return {
    formDialogVisible,
    loading,

    formData,
    schema,
    patchData,
    openForm,
    saveForm,
    cancelForm,
    resetFormData,
  } as const;
}
