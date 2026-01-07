import { ref, computed, unref } from "vue";
import type { UseFormService } from "~/form-system/types/serviceFormTypes";
import type { Field } from "~/components/types/form";
import { reportError } from "~/utils/errors/errors";
export function useFormCreate<
  I extends Record<string, any>,
  O extends Record<string, any>
>(
  getService: () => UseFormService<I, O>,
  getDefaultData: () => I | undefined | null,
  getFields: () => Field<I>[]
) {
  const service = computed(() => getService());
  const formDialogVisible = ref(false);
  const loading = ref(false);

  const safeDefaults = () => (getDefaultData?.() ?? {}) as I;

  const formData = ref<Partial<I>>({ ...safeDefaults() });
  const schema = computed(() => unref(getFields()));

  const resetFormData = async (data?: Partial<I>) => {
    formData.value = { ...safeDefaults(), ...(data ?? {}) };
  };

  const openForm = async (data?: Partial<I>) => {
    await resetFormData(data);
    formDialogVisible.value = true;
  };

  const saveForm = async (payload?: Partial<I>): Promise<I | null> => {
    if (!service.value.create) return null;

    loading.value = true;
    try {
      if (payload) formData.value = { ...formData.value, ...payload };

      const filteredData: Partial<I> = {};
      const collectKeys = (fields: Field<I>[]) => {
        fields.forEach((f) => {
          if (f.row) collectKeys(f.row);
          else if (f.key != null)
            filteredData[f.key] = (formData.value as any)[f.key] ?? null;
        });
      };
      collectKeys(unref(getFields()));

      const response = await service.value.create(filteredData as I);

      await resetFormData(response);
      formDialogVisible.value = false;

      return response;
    } catch (err) {
      reportError(err, "form.save.create_failed", "log");
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
