<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue";
// --------------------
// Page Meta
// --------------------
definePageMeta({
  layout: "admin",
});
// --------------------
// Base Components
// --------------------
import ActionButtons from "~/components/Button/ActionButtons.vue";
import Pagination from "~/components/TableEdit/Pagination/Pagination.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import BaseButton from "~/components/Base/BaseButton.vue";

// --------------------
// Composables
// --------------------
import { useDialogDynamicWidth } from "~/composables/useDialogDynamicWidth";
import { usePaginatedFetch } from "~/composables/pagination/usePaginatedFetch";
import { useInlineEdit } from "~/composables/inline-edit/useInlineEdit";

// --------------------
// Schemas & Registry
// --------------------
import { formRegistryCreate, formRegistryEdit } from "~/forms/admin/register";

// --------------------
// use dynamic form
// --------------------
import {
  useDynamicCreateFormReactive,
  useDynamicEditFormReactive,
  useInlineEditService,
} from "~/forms/dynamic/useAdminForms";
// --------------------
// Columns & Constants
// --------------------
import { userColumns } from "~/tables/columns/admin/userColumns";
import {
  roleOptions,
  roleStaffOptions,
  roleUserOptions,
} from "~/utils/constants/roles";

// --------------------
// API & Types
// --------------------
import type {
  AdminCreateUser,
  AdminGetUserData,
  AdminUpdateUser,
} from "~/api/admin/user/dto";
import type { AdminCreateStaff, AdminUpdateStaff } from "~/api/admin/staff/dto";

import { Role } from "~/api/types/enums/role.enum";

// --------------------
// Services
// --------------------

import { adminService } from "~/api/admin";

/* ----------------------------- types ----------------------------- */
type CreateMode = "USER" | "STAFF";
type EditMode = "USER" | "STAFF" | "STUDENT";
/* --------------------------- reactive ---------------------------- */
const isStaffMode = ref<boolean | undefined>(undefined);
const selectedRoles = ref<Role[]>([Role.STUDENT]);
const selectedFormCreate = ref<CreateMode>("USER");
const selectedFormEdit = ref<EditMode>("USER");
const editFormDataKey = ref("");

/* ---------------------------- create form -------------------------- */
const {
  formDialogVisible: createFormVisible,
  formData: createFormData,

  schema: createFormSchema,
  saveForm: saveCreateForm,
  cancelForm: cancelCreateForm,
  openForm: openCreateForm,
  loading: createFormLoading,
  resetFormData,
} = useDynamicCreateFormReactive(selectedFormCreate);

const handleOpenCreateForm = async () => {
  selectedFormCreate.value = isStaffMode.value ? "STAFF" : "USER";
  await openCreateForm();
};
const handleSaveCreateForm = (payload: Partial<any>) => {
  saveCreateForm(payload);
};
const handleCancelCreateForm = () => {
  cancelCreateForm();
};
watch(
  () => selectedFormCreate.value,
  () => {
    resetFormData(); // automatically uses the latest getDefaultData()
  }
);
/* ---------------------------- edit form -------------------------- */
const {
  formDialogVisible: editFormVisible,
  formData: editFormData,
  schema: editFormSchema,
  openForm: openEditForm,
  saveForm: saveEditForm,
  cancelForm: cancelEditForm,
  loading: editFormLoading,
} = useDynamicEditFormReactive(selectedFormEdit);

const handleOpenEditForm = async (row: AdminGetUserData) => {
  selectedFormEdit.value =
    row.role === "student"
      ? "STUDENT"
      : row.role === "academic" || row.role === "teacher"
      ? "STAFF"
      : "USER";
  editFormDataKey.value = row.id?.toString() ?? "new";
  editFormData.value = {};
  await nextTick();
  await openEditForm(row.id);
  editFormVisible.value = true;
};
const handleSaveEditForm = (payload: Partial<any>) => {
  saveEditForm(payload);
};
const handleCancelEditForm = () => {
  cancelEditForm();
};

/* ---------------------------- inline edit ------------------------ */
const {
  data,
  save,
  cancel,
  remove: removeUser,
  loading: inlineEditLoading,
  setData,
  autoSave,
  getPreviousValue,
  revertField,
} = useInlineEdit<AdminGetUserData, AdminUpdateUser>(
  [],
  useInlineEditService("USER")
);
const adminApiService = adminService();
/* ---------------------------- pagination ------------------------- */
const fetchUsers = async (
  rolesArray: Role[] | Ref<Role[]>,
  page: number,
  pageSize: number
) => {
  const roles = Array.isArray(rolesArray) ? rolesArray : rolesArray.value;
  const res = await adminApiService.user.getUserPage(roles, page, pageSize);

  const items = res?.users ?? [];
  const total = res?.total ?? 0;
  setData(items);

  return {
    items,
    total,
  };
};
const {
  loading: fetchLoading,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
} = usePaginatedFetch(fetchUsers, 1, 15, selectedRoles);

/* ----------------------------- misc ------------------------------ */
const currentRoleOptions = computed(() => {
  if (isStaffMode.value === true) return roleStaffOptions;
  if (isStaffMode.value === false) return roleUserOptions;
  return roleOptions;
});

watch(selectedRoles, () => fetchPage(1), { deep: true });
watch(isStaffMode, (mode) => {
  if (mode === true) {
    selectedFormCreate.value = "STAFF";
    selectedRoles.value = roleStaffOptions.map((r) => r.value);
  } else if (mode === false) {
    selectedFormCreate.value = "USER";
    selectedRoles.value = roleUserOptions.map((r) => r.value);
  } else {
    selectedFormCreate.value = "USER";
    selectedRoles.value = roleOptions.map((r) => r.value);
  }
  fetchPage(1);
});

/* --------------------------- computed -------------------------- */

const schemaCreate = computed(
  () => formRegistryCreate[selectedFormCreate.value].schema ?? []
);
const schemaEdit = computed(
  () => formRegistryEdit[selectedFormEdit.value].schema ?? []
);

const dynamicWidthCreate = computed(
  () => useDialogDynamicWidth(schemaCreate.value).value
);
const dynamicWidthEdit = computed(
  () => useDialogDynamicWidth(schemaEdit.value).value
);
/* ----------------------------- create form width ------------------------------ */

const createDialogWidth = computed(() => {
  if (selectedFormCreate.value === "STAFF") return "65%";
  if (selectedFormCreate.value === "USER") return "40%";
  return dynamicWidthCreate.value;
});

/* ----------------------------- edit form width ------------------------------ */

const editDialogWidth = computed(() => {
  if (selectedFormEdit.value === "STAFF") return "60%";
  if (selectedFormEdit.value === "STUDENT") return "70%";
  return dynamicWidthEdit.value;
});
const handleRevertField = (
  row: AdminGetUserData,
  field: keyof AdminGetUserData
) => {
  revertField(row, field);
};
onMounted(() => {
  selectedRoles.value = [
    Role.STUDENT,
    Role.TEACHER,
    Role.ACADEMIC,
    Role.PARENT,
  ];
});

function handleSaveWrapper(
  row: AdminGetUserData,
  field: keyof AdminGetUserData
) {
  if (field === "id") return;
  save(row, field as keyof AdminUpdateUser).catch((err) => {
    console.error(err);
  });
}
function handleAutoSaveWrapper(
  row: AdminGetUserData,
  field: keyof AdminGetUserData
) {
  if (field === "id") return;
  autoSave(row, field as keyof AdminUpdateUser).catch((err) => {
    console.error(err);
  });
}

const editFormDataTyped = computed({
  get: () => editFormData.value,
  set: (value) => (editFormData.value = value),
});
</script>

<template>
  <el-row class="m-2" justify="space-between">
    <el-col :span="12">
      <el-radio-group v-model="isStaffMode">
        <el-radio :value="undefined">Default</el-radio>
        <el-radio :value="false">User</el-radio>
        <el-radio :value="true">Staff</el-radio>
      </el-radio-group>
    </el-col>

    <el-col :span="12">
      <el-select
        v-model="selectedRoles"
        multiple
        filterable
        placeholder="Select roles"
        style="width: 300px"
      >
        <el-option
          v-for="opt in currentRoleOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </el-select>
    </el-col>
  </el-row>

  <el-row justify="space-between" class="m-4">
    <el-col :span="24">
      <BaseButton type="default" :loading="fetchLoading" @click="fetchPage(1)">
        Refresh
      </BaseButton>

      <BaseButton
        v-if="isStaffMode !== undefined"
        type="primary"
        @click="handleOpenCreateForm"
      >
        Add {{ isStaffMode ? "Staff" : "User" }}
      </BaseButton>
    </el-col>
  </el-row>

  <ErrorBoundary>
    <template #default>
      <SmartTable
        :data="data"
        :columns="userColumns"
        :loading="fetchLoading"
        @save="handleSaveWrapper"
        @cancel="cancel"
        @auto-save="handleAutoSaveWrapper"
      >
        <template #operation="{ row }">
          <ActionButtons
            :rowId="row.id"
            :role="row.role"
            :detailContent="`Edit ${
              row.role.charAt(0).toUpperCase() + row.role.slice(1)
            } details`"
            :deleteContent="`Delete ${
              row.role.charAt(0).toUpperCase() + row.role.slice(1)
            }`"
            :loading="inlineEditLoading[row.id] ?? false"
            @detail="handleOpenEditForm(row)"
            @delete="removeUser(row)"
          />
        </template>

        <template #controlsSlot="{ row, field }">
          <el-tooltip
            :content="`Previous: ${getPreviousValue(row, field)}`"
            placement="top"
          >
            <el-icon
              class="cursor-pointer"
              @click="handleRevertField(row, field)"
              ><Refresh
            /></el-icon>
          </el-tooltip>
        </template>
      </SmartTable>
    </template>
  </ErrorBoundary>

  <ErrorBoundary>
    <Pagination
      class-name="mt-6"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="totalRows"
      @page-change="goPage"
    />
  </ErrorBoundary>

  <!-- CREATE DIALOG -->
  <ErrorBoundary>
    <SmartFormDialog
      :key="selectedFormCreate"
      v-model:visible="createFormVisible"
      v-model="createFormData"
      :fields="createFormSchema"
      :title="`Add ${isStaffMode ? 'Staff' : 'User'}`"
      :loading="createFormLoading"
      @save="handleSaveCreateForm"
      @cancel="handleCancelCreateForm"
      :useElForm="true"
      :width="createDialogWidth"
    />
  </ErrorBoundary>

  <!-- EDIT DIALOG -->
  <ErrorBoundary>
    <SmartFormDialog
      :key="`${selectedFormEdit}-${editFormDataKey}`"
      v-model:visible="editFormVisible"
      v-model="editFormDataTyped"
      :fields="editFormSchema"
      :title="'Edit'"
      :loading="editFormLoading"
      @save="handleSaveEditForm"
      @cancel="handleCancelEditForm"
      :useElForm="true"
      :width="editDialogWidth"
    />
  </ErrorBoundary>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
