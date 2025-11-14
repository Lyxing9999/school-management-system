// composables/useFormCreate.ts
import { reactive, ref, computed, unref, nextTick } from "vue";
import type { FormInstance } from "element-plus";
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
  const elFormRef = ref<FormInstance>();

  // Reactive form data
  const formData = reactive<Partial<I>>({ ...getDefaultData() });

  // Computed schema
  const schema = computed(() => unref(getFields()));

  // Reset form to default + optional overrides
  const resetFormData = async (data?: Partial<I>) => {
    const defaults = getDefaultData();

    // Remove all old keys
    Object.keys(formData).forEach((key) => delete (formData as any)[key]);

    // Assign fresh defaults + overrides
    Object.assign(formData, { ...defaults, ...(data ?? {}) });
  };

  // Open form — ensure schema/data are updated first
  const openForm = async (data?: Partial<I>) => {
    console.log("before open getDefaultData ", getDefaultData());
    console.log("before open getFields ", getFields());
    console.log("before open elFormRef ", elFormRef.value);
    console.log("before open formDialogVisible ", formDialogVisible.value);
    resetFormData(data);

    console.log("after open getDefaultData ", getDefaultData());
    console.log("after open getFields ", getFields());
    console.log("after open elFormRef ", elFormRef.value);
    console.log("after open formDialogVisible ", formDialogVisible.value);
    formDialogVisible.value = true;
  };

  const saveForm = async (payload?: Partial<I>) => {
    if (!service.value.create) return;
    loading.value = true;
    try {
      if (payload) Object.assign(formData, payload);

      if (elFormRef.value) await elFormRef.value.validate();

      const filteredData: Partial<I> = {};
      const collectKeys = (fields: Field<I>[]) => {
        fields.forEach((f) => {
          if (f.row) collectKeys(f.row);
          else if (f.key != null) filteredData[f.key] = formData[f.key] ?? null;
        });
      };
      collectKeys(unref(getFields()));

      let response: I | null = null;
      try {
        response = await service.value.create(filteredData as I);
      } catch (err) {
        console.error("Create failed:", err);
        return;
      }

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
    schema,
    resetFormData,
    openForm,
    saveForm,
    cancelForm,
  } as const;
}
