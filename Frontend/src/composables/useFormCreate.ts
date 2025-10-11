// composables/useFormCreate.ts
import { ref, computed, unref, type Ref, type ComputedRef } from "vue";
import type { FormInstance } from "element-plus";
import type { UseFormService } from "~/services/types";
import type { Field } from "~/components/types/form";

export type InitialData<I> =
  | Partial<I>
  | Ref<Partial<I>>
  | ComputedRef<Partial<I>>;

export function useFormCreate<
  I extends Record<string, any>,
  O extends Record<string, any>
>(
  getService: () => UseFormService<I, O>,
  getDefaultData: () => I,
  getFields: () => Field<I>[]
) {
  const service = computed(() => getService());
  const formDialogVisible = ref(false);
  const loading = ref(false);
  const elFormRef = ref<FormInstance>();
  const formData = ref<Partial<I>>({ ...unref(getDefaultData()) });

  const resetFormData = (data?: Partial<I>) => {
    const schemaDefault = unref(getDefaultData());
    // remove keys not in default
    Object.keys(formData.value).forEach((key) => {
      if (!(key in schemaDefault)) delete (formData.value as any)[key];
    });
    Object.assign(formData.value, { ...schemaDefault, ...data });
  };

  const openForm = (data?: Partial<I>) => {
    resetFormData(data);
    formDialogVisible.value = true;
  };

  const saveForm = async (payload?: Partial<I>) => {
    if (!service.value.create) return;
    loading.value = true;
    try {
      if (elFormRef.value) await elFormRef.value.validate();

      if (payload) Object.assign(formData.value, payload);

      const fields = unref(getFields()) as Field<I>[];
      const filteredData: Partial<I> = {};

      // ✅ handle both single fields and row fields
      const collectKeys = (fields: Field<I>[]) => {
        fields.forEach((field) => {
          if (field.row) {
            // iterate row sub-fields
            collectKeys(field.row);
          } else if (field.key != null && field.key in formData.value) {
            filteredData[field.key] = formData.value[field.key];
          }
        });
      };

      collectKeys(fields);

      let response: I | null = null;

      try {
        response = await service.value.create(filteredData as I);
      } catch (err: any) {
        console.error("Create failed:", err);
        return; // stop, do not close dialog
      }

      // Only close if success
      if (response) {
        resetFormData(response);
        formDialogVisible.value = false;
      }
    } finally {
      loading.value = false;
    }
  };

  const cancelForm = () => {
    formDialogVisible.value = false;
    resetFormData();
  };

  return {
    formDialogVisible,
    loading,
    elFormRef,
    formData,
    resetFormData,
    openForm,
    saveForm,
    cancelForm,
  } as const;
}
