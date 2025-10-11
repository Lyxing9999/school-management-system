<script setup lang="ts">
import { ref, computed, watch, nextTick } from "vue";
import { useNuxtApp } from "nuxt/app";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import Pagination from "~/components/TableEdit/Pagination/Pagination.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import { useDialogDynamicWidth } from "~/composables/useDialogDynamicWidth";

definePageMeta({
  layout: "admin",
});
import { usePaginatedFetch } from "~/composables/pagination/usePaginatedFetch";
import {
  useInlineEdit,
  toInlineEditUpdateService,
} from "~/composables/inline-edit/useInlineEdit";

import { userColumns } from "~/schemas/columns/admin/userColumns";
import {
  roleOptions,
  roleStaffOptions,
  roleUserOptions,
} from "~/utils/constants/roles";
import {
  formRegistryCreate,
  formRegistryEdit,
} from "~/schemas/registry/AdminFormRegistry";

import { useFormEdit } from "~/composables/useFormEdit";
import { useFormCreate } from "~/composables/useFormCreate";

import type { AdminCreateUser, AdminGetUserData } from "~/api/admin/admin.dto";
import { Role } from "~/api/types/enums/role.enum";

/* ----------------------------- types ----------------------------- */
type CreateFields =
  (typeof formRegistryCreate)[keyof typeof formRegistryCreate]["schema"];
type EditFields =
  (typeof formRegistryEdit)[keyof typeof formRegistryEdit]["schema"];
type CreateMode = "USER" | "STAFF";
type EditMode = "USER" | "STAFF" | "STUDENT";
interface AdminEditable extends AdminGetUserData {
  id: string;
}
/* --------------------------- reactive ---------------------------- */
const isStaffMode = ref<boolean | undefined>(undefined);
const selectedRoles = ref<Role[]>([Role.STUDENT]);
const editFormKey = ref(0);
const selectedFormCreate = ref<CreateMode>("USER");
const selectedFormEdit = ref<EditMode>("USER");
const editFormDataKey = ref("");
/* --------------------------- registries -------------------------- */
const registryCreate = computed(
  () => formRegistryCreate[selectedFormCreate.value]
);

const registryEdit = computed(() => formRegistryEdit[selectedFormEdit.value]);
const registryCreateFormData = computed(() => registryCreate.value.formData());
/* --------------------------- create form ------------------------- */
/*
  Note: getFields must return the schema (Field<T>[]).
  useFormCreate signature (expected):
    useFormCreate(getService, initialData, getFields)
  where initialData is () => ({ ... }) and getFields is () => Field<T>[]
*/
const {
  formDialogVisible: createFormVisible,
  formData: createFormData,
  openForm: openCreateForm,
  saveForm: saveCreateForm,
  cancelForm: cancelCreateForm,
  resetFormData: resetCreateFormData,
  loading: createFormLoading,
} = useFormCreate(
  () => registryCreate.value.service,
  () => registryCreateFormData.value, // initial empty/default values
  () => registryCreate.value.schema as CreateFields
);

const handleOpenCreateForm = async () => {
  // pick schema before opening
  selectedFormCreate.value = isStaffMode.value ? "STAFF" : "USER";
  await nextTick();
  openCreateForm();
};

const handleSaveCreateForm = async (payload?: Partial<AdminCreateUser>) => {
  // composable saveForm returns boolean: true=success, false=failure
  await saveCreateForm(payload);

  // on success, you can refresh list
  fetchPage(1);
};

const handleCancelCreateForm = () => {
  cancelCreateForm(); // composable handles resetting + hiding
};

/* ---------------------------- edit form -------------------------- */
const {
  formDialogVisible: editFormVisible,
  formData: editFormData,
  openForm: openEditForm,
  saveForm: saveEditForm,
  cancelForm: cancelEditForm,
  resetFormData: resetEditFormData,
  loading: editFormLoading,
} = useFormEdit(
  () => registryEdit.value.service,
  () => registryEdit.value.schema as EditFields
);

const handleOpenEditForm = async (row: AdminGetUserData) => {
  if (row.role === "academic" || row.role === "teacher")
    selectedFormEdit.value = "STAFF";
  else if (row.role === "student") selectedFormEdit.value = "STUDENT";
  else selectedFormEdit.value = "USER";
  editFormKey.value++;
  editFormDataKey.value = row.id;

  await nextTick();
  await openEditForm(row.id);
};

const handleSaveEditForm = async (payload: Partial<any>) => {
  if (selectedFormEdit.value === "STUDENT") {
    await saveEditForm(payload);
  }
};

const handleCancelEditForm = () => {
  cancelEditForm();
};

/* ---------------------------- inline edit ------------------------ */
const registryInlineEdit = formRegistryEdit["USER"];
const inlineEditService = computed(() =>
  toInlineEditUpdateService<AdminGetUserData>(registryInlineEdit.service)
);

const {
  data,
  save,
  cancel,
  remove: removeUser,
  rowLoading,
  setData,
  autoSave,
  getPreviousValue,
  revertField,
} = useInlineEdit<AdminGetUserData>([], inlineEditService.value);

/* ---------------------------- pagination ------------------------- */
const { $adminService } = useNuxtApp();

const {
  loading: fetchLoading,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
} = usePaginatedFetch(
  async (roles: Role[], page: number, pageSize: number) => {
    const res = await $adminService.getUsers(roles, page, pageSize);
    setData(res?.users ?? []);
    return { items: res?.users ?? [], total: res?.total ?? 0 };
  },
  1,
  15,
  selectedRoles
);

/* ----------------------------- misc ------------------------------ */
const currentRoleOptions = computed(() => {
  if (isStaffMode.value === true) return roleStaffOptions;
  if (isStaffMode.value === false) return roleUserOptions;
  return roleOptions;
});

watch(selectedRoles, () => fetchPage(1), { deep: true });
watch(isStaffMode, (mode) => {
  if (mode === true) selectedRoles.value = roleStaffOptions.map((r) => r.value);
  else if (mode === false)
    selectedRoles.value = roleUserOptions.map((r) => r.value);
  fetchPage(1);
});

const createDialogWidth = computed(() => {
  const schema = registryCreate.value.schema;
  const width = useDialogDynamicWidth(schema).value;

  if (selectedFormCreate.value === "STAFF") return "80%";
  if (selectedFormCreate.value === "USER") return "40%";
  return width;
});
const editDialogWidth = computed(() => {
  const schema = registryEdit.value.schema;
  const width = useDialogDynamicWidth(schema).value;

  if (selectedFormEdit.value === "STAFF") return "60%";
  if (selectedFormEdit.value === "STUDENT") return "70%";
  return width;
});
</script>

<template>
  <el-row class="m-2" justify="space-between">
    <el-col :span="12">
      <el-radio-group v-model="isStaffMode">
        <el-radio :label="undefined">Default</el-radio>
        <el-radio :label="false">User</el-radio>
        <el-radio :label="true">Staff</el-radio>
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
        :smart-props="{ style: { width: '100%' }, rowLoading }"
        @save="save"
        @cancel="cancel"
        @auto-save="autoSave"
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
            :loading="rowLoading[row.id] ?? false"
            @detail="handleOpenEditForm(row)"
            @delete="handleDelete(row)"
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
      :fields="registryCreate.schema"
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
      :key="`${selectedFormEdit}-${editFormKey}-${editFormDataKey}`"
      v-model:visible="editFormVisible"
      v-model="editFormData"
      :fields="registryEdit.schema"
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
