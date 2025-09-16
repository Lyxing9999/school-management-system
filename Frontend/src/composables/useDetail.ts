import { ref, reactive } from "vue";

export function useDetail<T extends Record<string, any>>(
  service: {
    getDetail: (id: string | number) => Promise<T>;
    update: (data: T) => Promise<any>;
    delete?: (id: string | number) => Promise<any>;
  },
  formData: T
) {
  const detailDialogVisible = ref(false);
  const formDataEdit = reactive<Partial<T>>(formData);

  const openDetail = async (id: string | number) => {
    detailDialogVisible.value = true;
    const res = await service.getDetail(id);
    Object.assign(formDataEdit, res);
  };

  const saveDetail = async (data: Partial<T>, fetchPage?: () => void) => {
    await service.update(data as T);
    detailDialogVisible.value = false;
    if (fetchPage) fetchPage();
  };

  const cancelDetail = async () => {
    detailDialogVisible.value = false;
  };

  return {
    detailDialogVisible,
    formDataEdit,
    openDetail,
    saveDetail,
    cancelDetail,
  };
}
