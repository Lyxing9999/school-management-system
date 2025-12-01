// composables/useFormEdit.ts
import {
  ref,
  computed,
  unref,
  watch,
  toRaw,
  type Ref,
  type ComputedRef,
} from "vue";
import type { FormInstance } from "element-plus";
import type { UseFormService } from "~/forms/types/serviceFormTypes";
import type { Field } from "~/components/types/form";

export type InitialData<I> =
  | Partial<I>
  | Ref<Partial<I>>
  | ComputedRef<Partial<I>>;

type WithResult<T> = { result: T };

/**
 * useFormEdit
 * Handles dynamic edit/detail forms with patch/put/update support.
 * Defaults to PATCH on save.
 */
export function useFormEdit<I extends object, O extends I = I>(
  getService: () => UseFormService<undefined, I, undefined, O>,
  getDefaultData: () => I,
  getFields: () => Field<I>[]
) {
  const service = computed(() => getService());
  const formDialogVisible = ref(false);
  const loading = ref(false);
  const elFormRef = ref<FormInstance>();
  const saveId = ref<string | number>("");

  // current form state
  const formData = ref<Partial<I>>({});

  // original data loaded from API for this record
  const reactiveInitialData = ref<Partial<I>>({});

  // diff vs initial (for PATCH)
  const patchData = ref<Partial<I>>({});

  const schema = computed(() => unref(getFields()));
  const defaultData = computed(() => unref(getDefaultData()));

  /**
   * Track diffs: whenever formData changes, compute patchData compared to reactiveInitialData
   */
  watch(
    formData,
    (newVal) => {
      if (!newVal || typeof newVal !== "object") return;

      const fields = schema.value;
      fields.forEach((field) => {
        const fieldsToCheck = field.row ?? [field];

        fieldsToCheck.forEach((f) => {
          const key = f.key as keyof I;
          if (!key) return;

          const newValue = newVal[key];
          const oldValue = reactiveInitialData.value[key];

          if (newValue !== oldValue) {
            patchData.value[key] = newValue;
          } else {
            delete patchData.value[key];
          }
        });
      });
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
    patchData.value = {};
    formData.value = {};

    try {
      const detail = await service.value.getDetail(saveId.value.toString());
      const data = (
        detail && "result" in detail ? (detail as WithResult<O>).result : detail
      ) as Partial<I>;

      if (!data || Object.keys(data).length === 0) {
        reactiveInitialData.value = { ...defaultData.value };
        resetFormData(defaultData.value);
      } else {
        reactiveInitialData.value = toRaw(data);
        resetFormData(data);
      }

      // open after data is ready
      formDialogVisible.value = true;
    } finally {
      loading.value = false;
    }
  };
  /**
   * Save form — PATCH by default, PUT if method is explicitly set
   */
  const saveForm = async (
    payload: Partial<I>,
    method: "PATCH" | "PUT" = "PATCH"
  ): Promise<boolean> => {
    if (!service.value.update) return false;
    loading.value = true;

    try {
      // Validate form if a FormInstance is provided
      if (elFormRef.value) {
        await elFormRef.value.validate();
      }

      // Merge external payload (from SmartForm) into formData
      if (payload && Object.keys(payload).length > 0) {
        Object.assign(formData.value, payload);
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

      // Decide what to send:
      // - PATCH: use diff (patchData) when available, otherwise fall back to full filteredData
      // - PUT: always full filteredData
      let basePayload: Partial<I>;

      if (method === "PATCH") {
        const hasDiff = Object.keys(patchData.value).length > 0;
        basePayload = hasDiff ? (patchData.value as Partial<I>) : filteredData;
      } else {
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
      } catch (err) {
        console.error("Update failed:", err);
        return false;
      }

      if (response) {
        // Refresh initial data with response, reset form, close dialog
        reactiveInitialData.value = toRaw(response);
        resetFormData(response);
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
    // Optionally clear IDs/diffs so next open starts clean
    patchData.value = {};

    // Close dialog
    formDialogVisible.value = false;
  };

  return {
    formDialogVisible,
    loading,
    elFormRef,
    formData,
    schema,
    patchData,
    openForm,
    saveForm,
    cancelForm,
    resetFormData,
  } as const;
}
