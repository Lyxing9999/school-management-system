// composables/useFormCreate.ts
import { reactive, ref, computed, unref } from "vue";
import type { UseFormService } from "~/forms/types";
import type { Field } from "~/components/types/form";

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

  const formData = reactive<Partial<I>>({ ...getDefaultData() });
  const schema = computed(() => unref(getFields()));

  const resetFormData = async (data?: Partial<I>) => {
    const defaults = getDefaultData();
    Object.keys(formData).forEach((key) => delete (formData as any)[key]);
    Object.assign(formData, { ...defaults, ...(data ?? {}) });
  };

  const openForm = async (data?: Partial<I>) => {
    await resetFormData(data);
    formDialogVisible.value = true;
  };

  const saveForm = async (payload?: Partial<I>) => {
    if (!service.value.create) return;
    loading.value = true;

    try {
      if (payload) Object.assign(formData, payload);
      console.log("Form data before filtering:", formData);
      const filteredData: Partial<I> = {};
      const collectKeys = (fields: Field<I>[]) => {
        fields.forEach((f) => {
          if (f.row) collectKeys(f.row);
          else if (f.key != null)
            filteredData[f.key] =
              (formData as Record<string, any>)[f.key] ?? null;
        });
      };
      collectKeys(unref(getFields()));

      let response: I | null = null;
      try {
        console.log("this is filteredData", filteredData);
        response = await service.value.create(filteredData as I);
      } catch (err) {
        console.error("Create failed:", err);
        return;
      }

      if (response) {
        console.log("Response from create:", response);
        resetFormData(response);
        formDialogVisible.value = false;
      }
    } catch (err) {
      console.error("Create failed:", err);
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
    formData,
    schema,
    resetFormData,
    openForm,
    saveForm,
    cancelForm,
  } as const;
}
