<script setup lang="ts">
definePageMeta({ layout: "hr" });
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import SmartForm from "~/components/Form/SmartForm.vue";
import {
  employeeFormSchema,
  formData,
  formDataEditEmployee,
  employeeFormSchemaEdit,
} from "~/schemas/forms/hr/employeeForm";
import { employeeColumns } from "~/schemas/columns/hr/employeeColumns";
import { type AxiosInstance } from "axios";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import Pagination from "~/components/TableEdit/Pagination/Pagination.vue";
import { usePaginatedFetch } from "~/composables/pagination/usePaginatedFetch";
import { ref, onMounted } from "vue";
import { HrApi } from "~/api/hr/hr.api";
import { HrService } from "~/services/hrService";
import { useDetail } from "~/composables/useDetail";
import { useInlineEdit } from "~/composables/inline-edit/useInlineEdit";
const $api = useNuxtApp().$api;
const hrApi = new HrApi($api as AxiosInstance);
const hrService = new HrService(hrApi);

const {
  formDialogVisible,
  formData: createFormData,
  loading: createLoading,
  openForm,
  saveForm,
  cancelForm,
} = useForm(
  {
    create: (data: EmployeeCreateModel) => hrService.createEmployee(data),
  },
  formData,
  {
    onSuccess: () => fetchPage(),
    onError: (err: any) => console.error(err),
  }
);
const {
  detailDialogVisible,
  formDataEdit,
  openDetail,
  saveDetail,
  cancelDetail,
} = useDetail(hrService as any, formDataEditEmployee);

const { data, loading, currentPage, pageSize, totalRows, fetchPage, goPage } =
  usePaginatedFetch(
    async (page: number, pageSize: number) => {
      const res = await hrService.getEmployees(page, pageSize);
      setData(res.users);
      return { items: res.users, total: res.total };
    },
    1,
    15
  );
const {
  rowLoading,
  save,
  cancel,
  remove,
  setData,
  autoSave,
  getPreviousValue,
  revertField,
} = useInlineEdit<EmployeeReadModel>([], {
  update: (id: string, payload: EmployeeReadModel) =>
    hrService.updateEmployee(id, payload),
  remove: (id: string) => hrService.deleteEmployee(id),
});
onMounted(() => fetchPage());
</script>

<template>
  <BaseButton type="primary" class="m-6" @click="openForm"
    >Add Employee</BaseButton
  >
  <el-dialog v-model="formDialogVisible" title="Add New Employee" width="500px">
    <SmartForm
      :model-value="createFormData"
      :fields="employeeFormSchema"
      :useElForm="true"
      @save="saveForm"
      @cancel="cancelForm"
    />
  </el-dialog>

  <SmartTable
    class="mt-6"
    :columns="employeeColumns"
    :data="data"
    :loading="loading"
    :smart-props="{ style: { width: '100%' }, rowLoading }"
    @save="save"
    @cancel="cancel"
    @auto-save="autoSave"
  >
    <template #operation="{ row }">
      <ActionButtons
        :rowId="row.id"
        :onDetail="() => openDetail(row.id)"
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
  <el-dialog v-model="detailDialogVisible" width="600px" title="Edit Employee">
    <SmartForm
      :model-value="formDataEdit"
      :fields="employeeFormSchemaEdit"
      :useElForm="true"
      @save="saveDetail"
      @cancel="detailDialogVisible = false"
    />
  </el-dialog>
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
