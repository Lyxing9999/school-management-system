<script setup lang="ts">
import { ref, onMounted, watch, provide } from "vue";
import debounce from "lodash-es/debounce";

definePageMeta({ layout: "admin" });
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import { UsersHeader, UsersTable } from "~/components/pages/users";
import {
  useUserFilters,
  useUsersPaging,
  useUserStatusInline,
  useUserHeaderStats,
  useUserForms,
} from "~/composables/pages/users";

import { userColumns } from "~/modules/tables/columns/admin/userColumns";
import type {
  AdminGetUserItemData,
  AdminUpdateUser,
} from "~/api/admin/user/user.dto";

import { useInlineEdit } from "~/composables/useInlineEdit";
import { useInlineEditService } from "~/form-system/useDynamicForm.ts/useAdminForms";
import { Role } from "~/api/types/enums/role.enum";

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
  isDirty,
  resetAll,
} = useUserFilters();

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
} = useInlineEdit<AdminGetUserItemData, AdminUpdateUser>(
  [],
  useInlineEditService("USER")
);

/* 3) paging */
const {
  isFetching,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
  setPageSize,
  hasFetchedOnce,
} = useUsersPaging(filters, setInlineData);

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

/* init */
onMounted(async () => {
  selectedRoles.value = [
    Role.STUDENT,
    Role.TEACHER,
    Role.ACADEMIC,
    Role.PARENT,
  ];
  normalizeSelectedRoles();
  await fetchPage(1);
});

/* filter fetching */
const pendingFilterFetch = ref(false);

const debouncedRefresh = debounce(async () => {
  try {
    await fetchPage(1);
  } finally {
    pendingFilterFetch.value = false;
  }
}, 300);

watch(
  () => q.value,
  () => {
    pendingFilterFetch.value = true;
    debouncedRefresh();
  }
);

watch(
  selectedRoles,
  async () => {
    debouncedRefresh.cancel();
    pendingFilterFetch.value = true;
    try {
      await fetchPage(1);
    } finally {
      pendingFilterFetch.value = false;
    }
  },
  { deep: true }
);

watch(
  () => staffMode.value,
  async (mode, prev) => {
    if (mode === prev) return;

    selectedRoles.value = rolesFromMode(mode);
    normalizeSelectedRoles();

    debouncedRefresh.cancel();
    pendingFilterFetch.value = true;
    try {
      await fetchPage(1);
    } finally {
      pendingFilterFetch.value = false;
    }
  }
);

function handleOpenCreate() {
  openCreate(staffMode.value === "staff" ? "STAFF" : "STUDENT");
}
/* inline edit wrappers */
function handleSaveWrapper(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  if (field === "id") return;
  save(row, field as keyof AdminUpdateUser).catch(() => {});
}

function handleAutoSaveWrapper(
  row: AdminGetUserItemData,
  field: keyof AdminGetUserItemData
) {
  if (field === "id") return;
  autoSave(row, field as keyof AdminUpdateUser).catch(() => {});
}

/* header stats */
const { headerState: userHeaderStats } = useUserHeaderStats(
  totalRows,
  selectedRoles
);

provide("USER_ACTIONS", {
  onDelete: removeUser,
  onOpenEdit: openEdit,
});

provide("USER_STATE", {
  deleteLoading: deleteLoading,
  isDetailLoading: detailLoading,
});

function updateStatusDraft(val: any) {
  statusDraft.value = val;
}
</script>

<template>
  <div class="p-4 space-y-6">
    <UsersHeader
      :loading="isFetching"
      :stats="userHeaderStats"
      :isDirty="isDirty"
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
      :loading="isFetching || pendingFilterFetch"
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
      :getPreviousValue="getPreviousValue"
      @revert-field="revertField"
      @update-status-draft="updateStatusDraft"
      @start-edit-status="startEditStatus"
      @save-status="saveStatus"
      @cancel-edit-status="cancelEditStatus"
    />

    <el-row v-if="totalRows > 0" justify="end" class="mt-6">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="totalRows"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="goPage"
        @size-change="(size: number) => setPageSize(size)"
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
