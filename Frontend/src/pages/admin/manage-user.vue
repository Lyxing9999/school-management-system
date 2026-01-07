<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, provide, ref, watch } from "vue";
import debounce from "lodash-es/debounce";
import { usePreferencesStore } from "~/stores/preferencesStore";

definePageMeta({ layout: "default" });

import SmartFormDialog from "~/components/form/SmartFormDialog.vue";
import { UsersHeader, UsersTable } from "~/components/pages/users";
import {
  useUserFilters,
  useUsersPaging,
  useUserStatusInline,
  useUserHeaderStats,
  useUserForms,
  useUserResetPassword,
} from "~/composables/features/users";

import { userColumns } from "~/modules/tables/columns/admin/userColumns";
import type {
  AdminGetUserItemData,
  AdminUpdateUser,
} from "~/api/admin/user/user.dto";

import { useInlineEdit } from "~/composables/table-edit/useInlineEdit";
import { useInlineEditService } from "~/form-system/useDynamicForm.ts/useAdminForms";
import { Role } from "~/api/types/enums/role.enum";

const prefs = usePreferencesStore();

/* 1) filters */
const {
  q,
  staffMode,
  selectedRoles,
  currentRoleOptions,
  rolesFromMode,
  normalizeSelectedRoles,
  searchModel,
  filters,
  isDirty: filterDirty,
  resetAll,
} = useUserFilters();

selectedRoles.value = [Role.STUDENT, Role.TEACHER, Role.ACADEMIC, Role.PARENT];
normalizeSelectedRoles();

/* 2) inline edit */
const {
  data: rows,
  save,
  cancel,
  remove: removeUser,
  deleteLoading,
  inlineEditLoading,
  autoSave,
  getPreviousValue,
  revertField,
  setData: setInlineData,
  fieldErrors,
  getFieldError,
} = useInlineEdit<AdminGetUserItemData, AdminUpdateUser>(
  [],
  useInlineEditService("USER")
);

/* 3) paging */
const {
  loading,
  isFetching,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
  hasFetchedOnce,
} = useUsersPaging(filters, setInlineData);

pageSize.value = prefs.getTablePageSize();

/* 4) dialogs */
const {
  openCreate,
  openEdit,
  detailLoading,

  selectedFormCreate,
  createFormKey,
  createVisible,
  createData,
  createSchema,
  createLoading,
  saveCreateForm,
  cancelCreateForm,
  createDialogWidth,
  createDialogFullscreen,
  createDialogTop,

  selectedFormEdit,
  editFormDataKey,
  editVisible,
  editData,
  editSchema,
  editLoading,
  saveEditForm,
  cancelEditForm,
  editDialogWidth,
  editDialogFullscreen,
  editDialogTop,
} = useUserForms();

/* 5) status inline */
const {
  editingStatusRowId,
  statusDraft,
  statusSaving,
  statusTagType,
  formatStatusLabel,
  startEditStatus,
  cancelEditStatus,
  saveStatus,
} = useUserStatusInline();

const { handleResetPassword, resetLoading } = useUserResetPassword();

/* ---------------------------
   Refresh orchestration
--------------------------- */
const pendingFilterFetch = ref(false);
const tableLoading = computed(
  () => isFetching.value || pendingFilterFetch.value
);

const refreshFirstPage = async () => {
  pendingFilterFetch.value = true;
  try {
    await fetchPage(1);
  } finally {
    pendingFilterFetch.value = false;
  }
};

const refreshFirstPageDebounced = debounce(() => {
  void refreshFirstPage();
}, 300);

onBeforeUnmount(() => {
  refreshFirstPageDebounced.cancel();
});

/* init */
onMounted(async () => {
  await refreshFirstPage();
});

/* filter fetching */
watch(q, () => {
  pendingFilterFetch.value = true;
  refreshFirstPageDebounced();
});

watch(
  selectedRoles,
  async () => {
    refreshFirstPageDebounced.cancel();
    await refreshFirstPage();
  },
  { deep: true }
);

watch(staffMode, (mode, prev) => {
  if (mode === prev) return;
  refreshFirstPageDebounced.cancel();

  selectedRoles.value = [...rolesFromMode(mode)];
  normalizeSelectedRoles();
});

function handleOpenCreate() {
  openCreate(staffMode.value === "staff" ? "STAFF" : "STUDENT");
}

/* inline edit wrappers */
function handleSaveWrapper(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  if (field === "id") return;
  void save(row, field as keyof AdminUpdateUser).catch((err) => {
    reportError(err);
  });
}

function handleAutoSaveWrapper(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  if (field === "id") return;
  void autoSave(row, field as keyof AdminUpdateUser).catch((err) => {
    reportError(err);
  });
}

/* header stats */
const { headerState: userHeaderStats } = useUserHeaderStats(
  totalRows,
  selectedRoles
);

/* provide */
provide("USER_ACTIONS", {
  onDelete: removeUser,
  onOpenEdit: openEdit,
  onResetPassword: handleResetPassword,
});

provide("USER_STATE", {
  deleteLoading,
  isDetailLoading: detailLoading,
  inlineEditLoading,
  resetPasswordLoading: resetLoading,
});

function updateStatusDraft(val: typeof statusDraft.value) {
  statusDraft.value = val;
}

async function handlePageSizeChange(size: number) {
  prefs.setTablePageSize(size);
  pageSize.value = prefs.getTablePageSize();
  await fetchPage(1);
}

watch(
  () => prefs.tablePageSize,
  async () => {
    const next = prefs.getTablePageSize();
    if (pageSize.value === next) return;
    pageSize.value = next;
    await fetchPage(1);
  }
);
const pageSizes = computed<number[]>(() => [...prefs.ALLOWED_PAGE_SIZES]);
</script>

<template>
  <div class="p-4 space-y-6">
    <UsersHeader
      :loading="isFetching"
      :stats="userHeaderStats"
      :isDirty="filterDirty"
      v-model:staffMode="staffMode"
      v-model:selectedRoles="selectedRoles"
      v-model:searchModelValue="searchModel"
      :currentRoleOptions="currentRoleOptions"
      @refresh="fetchPage(currentPage)"
      @reset="resetAll"
      @open-create="handleOpenCreate"
    />

    <UsersTable
      :rows="rows"
      :columns="userColumns"
      :loading="tableLoading"
      :inline-edit-loading="inlineEditLoading"
      :has-fetched-once="hasFetchedOnce"
      :editingStatusRowId="editingStatusRowId"
      :statusDraft="statusDraft"
      :statusTagType="statusTagType"
      :formatStatusLabel="formatStatusLabel"
      :statusSaving="statusSaving"
      @save="handleSaveWrapper"
      @cancel="cancel"
      @auto-save="handleAutoSaveWrapper"
      @revert-field="revertField"
      @update-status-draft="updateStatusDraft"
      @start-edit-status="startEditStatus"
      @save-status="saveStatus"
      @cancel-edit-status="cancelEditStatus"
      @get-field-error="getFieldError"
      :getPreviousValue="getPreviousValue"
      :field-errors="fieldErrors"
    />

    <el-row v-if="totalRows > 0" justify="end" class="mt-6">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="pageSizes"
        :total="totalRows"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="goPage"
        @size-change="handlePageSizeChange"
      />
    </el-row>

    <!-- CREATE -->
    <SmartFormDialog
      :key="`${selectedFormCreate}-${createFormKey}`"
      v-model:visible="createVisible"
      v-model="createData"
      :fields="createSchema"
      :title="`Add ${staffMode === 'staff' ? 'Staff' : 'User'}`"
      :loading="createLoading"
      :useElForm="true"
      :fullscreen="createDialogFullscreen"
      :top="createDialogTop"
      :width="createDialogWidth"
      @save="
        async (payload) => {
          await saveCreateForm(payload);
          await fetchPage(currentPage);
        }
      "
      @cancel="cancelCreateForm"
    />

    <!-- EDIT -->
    <SmartFormDialog
      :key="`${selectedFormEdit}-${editFormDataKey}`"
      v-model:visible="editVisible"
      v-model="editData"
      :fields="editSchema"
      title="Edit"
      :loading="editLoading"
      :useElForm="true"
      :fullscreen="editDialogFullscreen"
      :top="editDialogTop"
      :width="editDialogWidth"
      @save="saveEditForm"
      @cancel="cancelEditForm"
    />
  </div>
</template>

<style scoped></style>
