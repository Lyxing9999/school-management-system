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
import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";

export type InitialData<I> =
  | Partial<I>
  | Ref<Partial<I>>
  | ComputedRef<Partial<I>>;

/**
 * useFormEdit
 * Handles dynamic edit/detail forms with patch/put/update support.
 * Defaults to PATCH on save.
 */
export function useFormEdit<I extends object, O extends I = I>(
  getService: () => UseFormService<I, O>,
  getFields: () => Field<I>[]
) {
  const service = computed(() => getService());
  const formDialogVisible = ref(false);
  const loading = ref(false);
  const elFormRef = ref<FormInstance>();
  const saveId = ref<string | number>("");
  const formData = ref<Partial<I>>({});
  const reactiveInitialData = ref<Partial<I>>({});
  const patchData = ref<Partial<I>>({});

  // Automatically track changes for PATCH
  watch(
    formData,
    (newVal) => {
      if (!newVal || typeof newVal !== "object") return;
      const fields = unref(getFields());
      fields.forEach((field) => {
        const key = field.key as keyof I;
        if (!key) return;

        const newValue = newVal[key];
        const oldValue = reactiveInitialData.value[key];

        if (newValue !== oldValue) patchData.value[key] = newValue;
        else delete patchData.value[key];
      });
    },
    { deep: true }
  );

  /** Reset form data (defaults to reactiveInitialData) */
  const resetFormData = (data?: Partial<I>) => {
    const safeInitial = reactiveInitialData.value || {};
    Object.keys(formData.value).forEach((key) => {
      if (!(key in safeInitial)) delete (formData.value as any)[key];
    });
    Object.assign(formData.value, { ...safeInitial, ...data });
  };
  /** Open form and load detail by ID */
  const openForm = async (id: string | number) => {
    if (!service.value?.getDetail) return;
    formDialogVisible.value = true;
    loading.value = true;
    saveId.value = id;
    try {
      const detail = await service.value.getDetail(saveId.value.toString());
      reactiveInitialData.value = toRaw(detail);
      resetFormData(detail);
    } finally {
      loading.value = false;
    }
  };

  /** Save form — PATCH by default, PUT if method is explicitly set */
  const saveForm = async (
    payload: Partial<I>,
    method: "PATCH" | "PUT" = "PATCH" // 👈 added optional method param
  ): Promise<boolean> => {
    if (!service.value.update) return false;
    loading.value = true;
    try {
      if (elFormRef.value) await elFormRef.value.validate();
      let response: I | null = null;
      if (payload) Object.assign(formData.value, payload);

      const fields = unref(getFields()) as Field<I>[];
      const filteredData: Partial<I> = {};

      fields.forEach((field) => {
        const key = field.key;
        if (key != null && key in formData.value) {
          filteredData[key] = formData.value[key];
        }
      });

      console.log("filteredData", filteredData);

      try {
        // ✅ use PUT if explicitly requested
        if (method === "PUT" && service.value.replace) {
          response = await service.value.replace(
            saveId.value.toString(),
            filteredData as O
          );
        } else {
          response = await service.value.update(
            saveId.value.toString(),
            filteredData as O
          );
        }
      } catch (err) {
        console.error("Update failed:", err);
        return false; // do NOT close dialog
      }

      if (response) {
        resetFormData(response);
        formDialogVisible.value = false;
        return true;
      }
      return false;
    } finally {
      loading.value = false;
    }
  };

  /** Cancel and reset */
  const cancelForm = () => {
    formDialogVisible.value = false;
    resetFormData();
  };

  return {
    formDialogVisible,
    loading,
    elFormRef,
    formData,
    patchData,
    openForm,
    saveForm,
    cancelForm,
    resetFormData,
  } as const;
}
