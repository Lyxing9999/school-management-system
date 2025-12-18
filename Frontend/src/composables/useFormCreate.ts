import { reactive, ref, computed, unref } from "vue";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";
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

  const saveForm = async (payload?: Partial<I>): Promise<I | null> => {
    if (!service.value.create) return null;

    loading.value = true;
    try {
      if (payload) Object.assign(formData, payload);

      const filteredData: Partial<I> = {};
      const collectKeys = (fields: Field<I>[]) => {
        fields.forEach((f) => {
          if (f.row) collectKeys(f.row);
          else if (f.key != null) {
            filteredData[f.key] =
              (formData as Record<string, any>)[f.key] ?? null;
          }
        });
      };
      collectKeys(unref(getFields()));

      const response = await service.value.create(filteredData as I);

      resetFormData(response);
      formDialogVisible.value = false;

      return response;
    } catch (err) {
      console.error("Create failed:", err);
      return null;
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
