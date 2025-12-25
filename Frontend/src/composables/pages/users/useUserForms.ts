import { ref, computed, nextTick, watch } from "vue";
import {
  adminFormRegistryCreate,
  adminFormRegistryEdit,
} from "~/form-system/register/admin";
import { useDialogDynamicWidth } from "~/composables/useDialogDynamicWidth";
import {
  useDynamicCreateFormReactive,
  useDynamicEditFormReactive,
} from "~/form-system/useDynamicForm.ts/useAdminForms";
import type { AdminGetUserItemData } from "~/api/admin/user/user.dto";

type CreateMode = "STAFF" | "STUDENT";
type EditMode = "STAFF" | "STUDENT";

export function useUserForms() {
  // CREATE
  const selectedFormCreate = ref<CreateMode>("STUDENT");
  const createFormKey = ref(0);
  const create = useDynamicCreateFormReactive(selectedFormCreate);

  async function openCreate(mode: CreateMode) {
    selectedFormCreate.value = mode;
    createFormKey.value++;

    await nextTick();
    await create.openForm();
  }

  const schemaCreate = computed(
    () => adminFormRegistryCreate[selectedFormCreate.value].schema ?? []
  );
  const createWidthRef = useDialogDynamicWidth(schemaCreate.value);

  const createDialogWidth = computed(() => {
    if (selectedFormCreate.value === "STAFF") return "65%";
    if (selectedFormCreate.value === "STUDENT") return "80%";
    return createWidthRef.value;
  });

  // EDIT (unchanged – your pattern is OK)
  const selectedFormEdit = ref<EditMode>("STUDENT");
  const editFormDataKey = ref<string>("");
  const detailLoadingMap = ref<Record<string, boolean>>({});
  const edit = useDynamicEditFormReactive(selectedFormEdit);

  function detailLoading(id: string | number) {
    return !!detailLoadingMap.value[String(id)];
  }

  async function openEdit(row: AdminGetUserItemData) {
    const key = String(row.id);
    try {
      detailLoadingMap.value[key] = true;
      selectedFormEdit.value = row.role === "student" ? "STUDENT" : "STAFF";
      editFormDataKey.value = key || "new";

      await nextTick();
      await edit.openForm(row.id);
    } finally {
      detailLoadingMap.value[key] = false;
    }
  }

  const schemaEdit = computed(
    () => adminFormRegistryEdit[selectedFormEdit.value].schema ?? []
  );
  const editWidthRef = useDialogDynamicWidth(schemaEdit.value);

  const editDialogWidth = computed(() => {
    if (selectedFormEdit.value === "STAFF") return "60%";
    if (selectedFormEdit.value === "STUDENT") return "70%";
    return editWidthRef.value;
  });

  return {
    openCreate,
    openEdit,
    detailLoading,

    selectedFormCreate,
    createFormKey,
    createVisible: create.formDialogVisible,
    createData: create.formData,
    createSchema: create.schema,
    createLoading: create.loading,
    saveCreateForm: create.saveForm,
    cancelCreateForm: create.cancelForm,
    createDialogWidth,

    selectedFormEdit,
    editFormDataKey,
    editVisible: edit.formDialogVisible,
    editData: edit.formData,
    editSchema: edit.schema,
    editLoading: edit.loading,
    saveEditForm: edit.saveForm,
    cancelEditForm: edit.cancelForm,
    editDialogWidth,
  };
}
