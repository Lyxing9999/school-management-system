<script setup lang="ts">
definePageMeta({
  layout: "academic",
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
import { usePaginatedFetch } from "~/composables/pagination/usePaginatedFetch";
import { useInlineEdit } from "~/composables/inline-edit/useInlineEdit";

import { userColumns } from "~/schemas/columns/admin/userColumns";

// --------------------
// Schemas & Registry
// --------------------
import {
  academicFormRegistry,
  formRegistryEdit,
  formRegistryCreate,
  inlineEditService,
  useEditForm,
  useCreateForm,
} from "~/schemas/registry/AcademicFormRegistry";
import { useFormCreate } from "~/composables/useFormCreate";
import { useFormEdit } from "~/composables/useFormEdit";
// --- wrapper for fetching students ---
import type {
  AcademicCreateStudentData,
  AcademicStudentData,
  AcademicUpdateStudentData,
} from "~/api/academic/academic.dto";

const editFormDataKey = ref("");
const {
  data,
  save,
  cancel,
  autoSave,
  remove: removeUser,
  setData,
  getPreviousValue,
  revertField,
  loading: inlineEditLoading,
} = useInlineEdit<AcademicStudentData>([], inlineEditService.value);

/* ---------------------------- pagination ------------------------- */
const fetchStudents = async (
  _filter: undefined,
  page: number,
  pageSize: number
) => {
  const res = await academicFormRegistry.studentIAM.list!({ page, pageSize });
  setData(res.items);
  return {
    items: res.items,
    total: res.total,
  };
};
const {
  loading: fetchLoading,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
} = usePaginatedFetch(fetchStudents);
// create form
const {
  formDialogVisible: createFormVisible,
  loading: createFormLoading,
  openForm: openCreateForm,
  formData: createFormData,
  schema: createFormSchema,
  saveForm: saveCreateForm,
  cancelForm: cancelCreateForm,
} = useCreateForm();
const handleOpenCreateForm = () => {
  openCreateForm();
};

const handleSaveCreateForm = (payload: Partial<AcademicCreateStudentData>) => {
  saveCreateForm(payload);
};

const handleCancelCreateForm = () => {
  cancelCreateForm();
};

// edit form
const {
  formDialogVisible: editFormVisible,
  loading: editFormLoading,
  openForm: openEditForm,
  schema: editFormSchema,
  formData: editFormData,
  saveForm: saveEditForm,
  cancelForm: cancelEditForm,
} = useEditForm();

const handleOpenEditForm = async (row: AcademicStudentData) => {
  editFormDataKey.value = row.id?.toString() ?? "new";
  editFormData.value = {};
  await nextTick();
  await openEditForm(row.id);
  editFormVisible.value = true;
};
const handleSaveEditForm = (payload: AcademicUpdateStudentData) => {
  saveEditForm(payload as any);
};
const handleCancelEditForm = () => {
  cancelEditForm();
};

onMounted(() => {
  fetchPage(1);
});
</script>

<template>
  <BaseButton @click="handleOpenCreateForm">Add Student</BaseButton>
  <div class="p-4">
    <SmartTable
      :data="data"
      :columns="userColumns"
      :loading="fetchLoading"
      :smart-props="{ style: { width: '100%' }, inlineEditLoading }"
      @edit-save="save"
      @edit-cancel="cancel"
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
          <el-icon class="cursor-pointer" @click="revertField(row, field)"
            ><Refresh
          /></el-icon>
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

    <!-- CREATE DIALOG -->
    <ErrorBoundary>
      <SmartFormDialog
        v-model:visible="createFormVisible"
        v-model="createFormData"
        :fields="createFormSchema"
        :loading="createFormLoading"
        @save="handleSaveCreateForm"
        @cancel="handleCancelCreateForm"
        :useElForm="true"
        :width="'400px'"
      />
    </ErrorBoundary>

    <!-- EDIT DIALOG -->
    <ErrorBoundary>
      <SmartFormDialog
        :key="editFormDataKey"
        v-model:visible="editFormVisible"
        v-model="editFormData"
        :fields="editFormSchema"
        :title="'Edit'"
        :loading="editFormLoading"
        @save="handleSaveEditForm"
        @cancel="handleCancelEditForm"
        :useElForm="true"
        :width="'70%'"
        :style="{ maxWidth: '1000px' }"
      />
    </ErrorBoundary>
  </div>
</template>

<style scoped>
/* Optional styling */
</style>
