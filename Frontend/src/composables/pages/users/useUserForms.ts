import { ref, computed, nextTick } from "vue";
import { useDialogDynamicWidth } from "~/composables/useDialogDynamicWidth";
import { useResponsiveDialog } from "~/composables/useResponsiveDialog";
import {
  useDynamicCreateFormReactive,
  useDynamicEditFormReactive,
} from "~/form-system/useDynamicForm.ts/useAdminForms";
import {
  adminFormRegistryCreate,
  adminFormRegistryEdit,
} from "~/form-system/register/admin";
import type { AdminGetUserItemData } from "~/api/admin/user/user.dto";

type CreateMode = "STAFF" | "STUDENT";
type EditMode = "STAFF" | "STUDENT";

export function useUserForms() {
  const dialog = useResponsiveDialog({
    mobileBp: 768,
    preset: { desktopMinPx: 560, desktopVw: 72, desktopMaxPx: 1040 },
  });
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

  // IMPORTANT: pass the computed ref, not schemaCreate.value
  const createWidthBySchema = useDialogDynamicWidth(schemaCreate);

  // One responsive “policy”
  const createResponsive = useResponsiveDialog({
    preset: {
      desktopMinPx: 560,
      desktopVw: selectedFormCreate.value === "STAFF" ? 62 : 74,
      desktopMaxPx: selectedFormCreate.value === "STAFF" ? 920 : 1020,
    },
  });

  const createDialogWidth = computed(() => {
    if (dialog.isMobile.value) return "100%";

    // CTO-style: explicit clamp per form type (predictable)
    if (selectedFormCreate.value === "STAFF") {
      return "clamp(560px, 65vw, 980px)";
    }
    return "clamp(560px, 78vw, 1120px)";
  });

  // EDIT
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

  const editWidthBySchema = useDialogDynamicWidth(schemaEdit);
  const editResponsive = useResponsiveDialog({
    preset: {
      desktopMinPx: 540,
      desktopVw: selectedFormEdit.value === "STAFF" ? 60 : 70,
      desktopMaxPx: selectedFormEdit.value === "STAFF" ? 880 : 980,
    },
  });

  const editDialogWidth = computed(() => {
    if (dialog.isMobile.value) return "100%";
    if (selectedFormEdit.value === "STAFF") {
      return "clamp(560px, 60vw, 960px)";
    }
    return "clamp(560px, 72vw, 1080px)";
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
    createDialogFullscreen: createResponsive.fullscreen,
    createDialogTop: createResponsive.top,

    selectedFormEdit,
    editFormDataKey,
    editVisible: edit.formDialogVisible,
    editData: edit.formData,
    editSchema: edit.schema,
    editLoading: edit.loading,
    saveEditForm: edit.saveForm,
    cancelEditForm: edit.cancelForm,
    editDialogWidth,
    editDialogFullscreen: editResponsive.fullscreen,
    editDialogTop: editResponsive.top,
  };
}
