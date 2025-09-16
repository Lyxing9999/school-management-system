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
// Page meta
definePageMeta({ layout: "admin" });

// API & Service
const $api = useNuxtApp().$api as AxiosInstance;
const adminApi = new AdminApi($api);
const adminService = new AdminService(adminApi);

// Inline editing
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

const roleOptions = [
  { value: "academic", label: "Academic" },
  { value: "hr", label: "HR" },
  { value: "admin", label: "Admin" },
  { value: "student", label: "Student" },
];

const {
  loading,
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
  loading.value = true;
  await fetchPage();
  loading.value = false;
});
onMounted(() => fetchPage());
</script>

<template>
  <el-select
    v-model="selectedRoles"
    multiple
    filterable
    placeholder="Select roles"
    style="width: 300px"
  >
    <el-option
      v-for="opt in roleOptions"
      :key="opt.value"
      :label="opt.label"
      :value="opt.value"
    />
  </el-select>
  <SmartTable
    :data="data"
    :columns="userColumns"
    :loading="loading"
    :smart-props="{ style: { width: '100%' }, rowLoading }"
    @save="save"
    @cancel="cancel"
    @auto-save="autoSave"
  >
    <template #operation="{ row }">
      <ActionButtons
        :rowId="row.id"
        :loading="rowLoading[row.id] ?? false"
        :onDetail="() => {}"
        :onDelete="() => remove(row)"
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
</template>
<style scoped>
:deep(.el-input-group__append) {
  padding: 0 10px;
}
</style>
