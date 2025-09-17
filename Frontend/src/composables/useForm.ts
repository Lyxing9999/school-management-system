// composables/useForm.ts
import { ref, reactive } from "vue";
import type { FormInstance } from "element-plus";

export function useForm<T extends Record<string, any>>(
  service: {
    create: (data: T) => Promise<any>;
    update?: (data: T) => Promise<any>;
    delete?: (id: string | number) => Promise<any>;
  },
  initialData: T,
  options?: {
    onSuccess?: () => void;
    onError?: (err: any) => void;
  }
) {
  const formDialogVisible = ref(false);
  const formData = reactive<Partial<T>>({ ...initialData });
  const loading = ref(false);

  const openForm = () => {
    formDialogVisible.value = true;
    Object.assign(formData, initialData);
  };

  const saveForm = async (
    form: Record<string, any>,
    elFormRef?: FormInstance
  ) => {
    loading.value = true;
    try {
      if (elFormRef) {
        await elFormRef.validate();
      }
      await service.create(form as T);
      formDialogVisible.value = false;
      options?.onSuccess?.();
    } catch (err) {
      options?.onError?.(err);
      console.error(err);
    } finally {
      loading.value = false;
    }
  };

  const cancelForm = () => {
    formDialogVisible.value = false;
  };

  return {
    formDialogVisible,
    formData,
    loading,
    openForm,
    saveForm,
    cancelForm,
  };
}
