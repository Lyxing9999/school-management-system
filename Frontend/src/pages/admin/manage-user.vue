<script setup lang="ts">
import { onMounted, ref, reactive, computed, toRaw } from "vue";
import { useNuxtApp } from "nuxt/app";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import Pagination from "~/components/TableEdit/Pagination/Pagination.vue";
import { userColumns } from "~/schemas/columns/admin/userColumns";
import { AdminApi } from "~/api/admin/admin.api";
import { AdminService } from "~/services/adminService";
import { usePaginatedFetch } from "~/composables/pagination/usePaginatedFetch";
import { useInlineEdit } from "~/composables/inline-edit/useInlineEdit";
import SmartForm from "~/components/Form/SmartForm.vue";
import { useForm } from "~/composables/useForm";
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import { userFormSchema, userFormData } from "~/schemas/forms/admin/userForm";
import {
  staffFormSchema,
  staffFormData,
} from "~/schemas/forms/admin/staffFrom";
import type { Role } from "~/api/types/enums/role.enum";
import type { AxiosInstance } from "axios";
import type { AdminGetUserData } from "~/api/admin/admin.dto";

definePageMeta({ layout: "admin" });

const $api = useNuxtApp().$api as AxiosInstance;
const adminApi = new AdminApi($api);
const adminService = new AdminService(adminApi);

const isStaffMode = ref<boolean | undefined>(undefined);

// Inline Edit
const {
  data,
  save,
  cancel,
  remove,
  rowLoading,
  setData,
  autoSave,
  getPreviousValue,
  revertField,
} = useInlineEdit<AdminGetUserData>([], {
  update: (id, payload) => {
    if (isStaffMode.value)
      return adminService.updateStaff(id.toString(), payload as any);
    return adminService.updateUser(id.toString(), payload as any);
  },
  remove: async (id) => {
    await adminService.deleteUser(id.toString());
  },
});

// Pagination
const {
  loading: fetchLoading,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
  selectedRoles,
  currentRoleOptions,
} = usePaginatedFetch(
  async (roles: Role[], page: number, pageSize: number) => {
    const res = await adminService.getUsers(roles, page, pageSize);
    setData(res?.users ?? []);
    return { items: res?.users ?? [], total: res?.total ?? 0 };
  },
  1,
  15,
  isStaffMode
);

// -------------------------
// useForm
// -------------------------
const {
  formDialogVisible,
  formData,
  loading: createLoading,
  saveForm,
  cancelForm,
} = useForm(
  {
    create: async (data) => {
      const payload = { ...toRaw(data) };
      if (isStaffMode.value) return adminService.createStaff(payload);
      return adminService.createUser(payload);
    },
  },
  {}, // start empty, will populate when opening
  { onError: (err) => console.error(err) }
);

// Open form correctly
function handleOpenForm() {
  const initialData = isStaffMode.value
    ? toRaw(staffFormData)
    : toRaw(userFormData);
  Object.assign(formData, initialData); // populate reactive formData
  formDialogVisible.value = true;
}

// Inline edit helpers
function handleRevertField(row: any, field: string) {
  revertField(row, field as keyof AdminGetUserData);
}

function handleDelete(rowId: AdminGetUserData) {
  remove(rowId);
}

function handleDetail(rowId: string | number) {
  console.log("Detail", rowId);
}

const handleRefresh = () => fetchPage();

onMounted(async () => {
  await fetchPage();
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
      <BaseButton type="default" :loading="fetchLoading" @click="handleRefresh">
        Refresh
      </BaseButton>
      <BaseButton
        v-if="isStaffMode !== undefined"
        type="primary"
        @click="handleOpenForm"
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
            :hideDetailForRoles="['student']"
            :loading="rowLoading[row.id] ?? false"
            @detail="handleDetail(row.id)"
            @delete="handleDelete(row.id)"
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
            >
              <Refresh />
            </el-icon>
          </el-tooltip>
        </template>
      </SmartTable>
    </template>
  </ErrorBoundary>

  <ErrorBoundary>
    <template #default>
      <Pagination
        class-name="mt-6"
        :current-page="currentPage"
        :page-size="pageSize"
        :total="totalRows"
        @page-change="goPage"
      />
    </template>
  </ErrorBoundary>

  <ErrorBoundary>
    <template #default>
      <el-dialog v-model="formDialogVisible" title="Add New User" width="500px">
        <SmartForm
          :model-value="formData"
          :fields="isStaffMode ? staffFormSchema : userFormSchema"
          :loading="createLoading"
          @save="saveForm"
          @cancel="cancelForm"
          :useElForm="true"
        />
      </el-dialog>
    </template>
  </ErrorBoundary>
</template>

<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
