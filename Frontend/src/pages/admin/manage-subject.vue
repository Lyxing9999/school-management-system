<script setup lang="ts">
import { ref, nextTick } from "vue";
import { ElMessage } from "element-plus";

definePageMeta({ layout: "admin" });

import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import { subjectColumns } from "~/schemas/columns/admin/subjectColumns";
import {
  useDynamicCreateFormReactive,
  useDynamicEditFormReactive,
} from "~/schemas/registry/admin/formDynamic";
import type { BaseSubject } from "~/api/types/subject.dto";
import type {
  AdminCreateSubject,
  AdminUpdateSubject,
} from "~/api/admin/admin.dto";
import { serviceSubject } from "~/services/formServices/adminFormService";

// State
const subjects = ref<BaseSubject[]>([]);
const loading = ref(false);
const editFormDataKey = ref("");

// Create Form
const {
  formDialogVisible: createVisible,
  formData: createData,
  schema: createSchema,
  openForm: openCreate,
  saveForm: saveCreate,
  cancelForm: cancelCreate,
  loading: createLoading,
} = useDynamicCreateFormReactive(ref("SUBJECT"));

// Edit Form
const {
  formDialogVisible: editVisible,
  formData: editData,
  schema: editSchema,
  openForm: openEdit,
  saveForm: saveEdit,
  cancelForm: cancelEdit,
  loading: editLoading,
} = useDynamicEditFormReactive(ref("SUBJECT"));

// Fetch Data
const fetchSubjects = async () => {
  loading.value = true;
  try {
    subjects.value = (await serviceSubject.all?.()) ?? [];
  } finally {
    loading.value = false;
  }
};

// Handlers
const handleCreate = async () => {
  await nextTick();
  openCreate();
};

const handleSaveCreate = async (payload: Partial<AdminCreateSubject>) => {
  await saveCreate(payload);
  ElMessage.success("Subject created successfully");
  fetchSubjects();
};

const handleEdit = async (row: BaseSubject) => {
  editFormDataKey.value = row.id?.toString() ?? "new";
  editData.value = {};
  await nextTick();
  await openEdit(row.id);
  editVisible.value = true;
};

const handleSaveEdit = async (payload: Partial<AdminUpdateSubject>) => {
  await saveEdit(payload);
  ElMessage.success("Subject updated successfully");
  fetchSubjects();
};

// Initialize
fetchSubjects();
</script>

<template>
  <div class="subject-page">
    <div class="page-header">
      <h1 class="page-title">Subjects</h1>
      <BaseButton type="primary" @click="handleCreate">
        Add Subject
      </BaseButton>
    </div>

    <div class="table-container">
      <SmartTable
        :data="subjects"
        :columns="subjectColumns"
        :loading="loading"
        row-key="id"
        @edit="handleEdit"
      />
    </div>

    <SmartFormDialog
      v-model:visible="createVisible"
      v-model="createData"
      :fields="createSchema"
      :loading="createLoading"
      title="Add Subject"
      width="50%"
      use-el-form
      @save="handleSaveCreate"
      @cancel="cancelCreate"
    />

    <SmartFormDialog
      :key="`edit-${editFormDataKey}`"
      v-model:visible="editVisible"
      v-model="editData"
      :fields="editSchema"
      :loading="editLoading"
      title="Edit Subject"
      width="50%"
      use-el-form
      @save="handleSaveEdit"
      @cancel="cancelEdit"
    />
  </div>
</template>

<style scoped>
.subject-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.table-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
