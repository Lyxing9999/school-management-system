<script setup lang="ts">
import { onMounted } from "vue";
import { useNuxtApp } from "nuxt/app";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import Pagination from "~/components/TableEdit/Pagination/Pagination.vue";
import { userColumns } from "~/schemas/columns/admin/userColumns";
import type { AxiosInstance } from "axios";
import { AdminApi } from "~/api/admin/admin.api";
import { AdminService } from "~/services/adminService";
import { usePaginatedFetch } from "~/composables/pagination/usePaginatedFetch";
import { useInlineEdit } from "~/composables/inline-edit/useInlineEdit";
import type { AdminGetUserData } from "~/api/admin/admin.dto";
import type { Role } from "~/api/types/enums/role.enum";
import SmartForm from "~/components/Form/SmartForm.vue";
definePageMeta({ layout: "admin" });
import { roleStaffOptions } from "~/utils/constants/roles";
import { useForm } from "~/composables/useForm";
import type { AdminCreateUser } from "~/api/admin/admin.dto";
import { userFormSchema, userFormData } from "~/schemas/forms/admin/userForm";
const $api = useNuxtApp().$api as AxiosInstance;
const adminApi = new AdminApi($api);
const adminService = new AdminService(adminApi);

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
  update: (id: string | number, payload: Partial<AdminGetUserData>) =>
    adminService.updateUser(id.toString(), payload),
  remove: async (id: string | number) => {
    await adminService.deleteUser(id.toString());
  },
});

const {
  loading: fetchLoading,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
  selectedRoles,
} = usePaginatedFetch(
  async (roles: Role | Role[], page: number, pageSize: number) => {
    const res = await adminService.getUsers(roles, page, pageSize);
    setData(res?.users ?? []);
    return {
      items: res?.users ?? [],
      total: res?.total ?? 0,
    };
  },
  1,
  15
);

watch(selectedRoles, async () => {
  fetchLoading.value = true;
  await fetchPage();
  fetchLoading.value = false;
});

const {
  formDialogVisible,
  formData,
  loading: createLoading,
  openForm,
  saveForm,
  cancelForm,
} = useForm(
  {
    create: (data: AdminCreateUser) => adminService.createUser(data),
  },
  userFormData,
  {
    onError: (err: any) => console.error(err),
  }
);
</script>

<template>
  <el-form-item label="Active">
    <el-switch
      v-model="formData.isActive"
      active-color="#13ce66"
      inactive-color="#ff4949"
    />
  </el-form-item>
  <el-row class="m-10" justify="space-between">
    <el-col :span="12">
      <BaseButton type="primary" @click="openForm">Add Staff</BaseButton>
    </el-col>
    <el-col :span="12" align="right">
      <el-select
        v-model="selectedRoles"
        multiple
        filterable
        placeholder="Select roles"
        style="width: 300px"
      >
        <el-option
          v-for="opt in roleStaffOptions"
          :key="opt.value"
          :label="opt.label"
          :value="opt.value"
        />
      </el-select>
    </el-col>
  </el-row>
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
        :onDetail="() => console.log('Detail', row.id)"
        :onDelete="() => remove(row.id)"
      />
    </template>
    <template #controlsSlot="{ row, field }">
      <el-tooltip
        :content="`Previous: ${getPreviousValue(row, field)}`"
        placement="top"
      >
        <el-icon class="cursor-pointer" @click="() => revertField(row, field)">
          <Refresh />
        </el-icon>
      </el-tooltip>
    </template>
  </SmartTable>

  <Pagination
    class-name="mt-6"
    :current-page="currentPage"
    :page-size="pageSize"
    :total="totalRows"
    @page-change="goPage"
  />
  <el-dialog v-model="formDialogVisible" title="Add New User" width="500px">
    <SmartForm
      :model-value="formData"
      :fields="userFormSchema"
      :loading="createLoading"
      @save="saveForm"
      @cancel="cancelForm"
      :useElForm="true"
    />
  </el-dialog>
</template>
<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
