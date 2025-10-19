<!-- Page Component -->
<script lang="ts" setup>
import { ref, onMounted } from "vue";
import { classColumns } from "~/schemas/columns/academic/classColumns";
import { serviceClass } from "~/services/formServices/adminFormService";
// --------------------
// Base Components
// --------------------
import ActionButtons from "~/components/Button/ActionButtons.vue";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
// --------------------
// Type Components
// --------------------
import type { BaseClassDataDTO } from "~/api/types/baseClass";

import { useInlineEditService } from "~/schemas/registry/formDynamic";
import { useInlineEdit } from "~/composables/inline-edit/useInlineEdit";
import type { AdminUpdateClass } from "~/api/admin/admin.dto";
const classes = ref<BaseClassDataDTO[]>([]);

// Fetch classes
const fetchClasses = async () => {
  const res = await serviceClass.all!({});
  classes.value = res;
};

onMounted(() => {
  fetchClasses();
});

const {
  save,
  cancel,
  remove,
  autoSave,
  data,
  setData,
  getPreviousValue,
  revertField,
} = useInlineEdit<BaseClassDataDTO, AdminUpdateClass>(
  [],
  useInlineEditService("CLASS")
);
definePageMeta({
  layout: "admin",
});

onMounted(() => {
  fetchClasses();
});
</script>

<template>
  <div
    class="bg-gradient-to-r from-gray-50 to-white rounded-2xl px-10 py-6 mb-8"
    style="
      box-shadow: 0 4px 12px rgba(123, 63, 160, 0.2); /* subtle primary color shadow */
    "
  >
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-semibold text-gray-800 leading-tight">
          Classes Management
        </h2>
        <p class="text-gray-500 text-base mt-1">
          Manage school classes and assign subjects
        </p>
      </div>

      <BaseButton
        type="primary"
        size="large"
        class="shrink-0 flex items-center gap-2"
        @click="openCreateClassModal"
      >
        <el-icon><Plus /></el-icon>
        Add Class
      </BaseButton>
    </div>
  </div>
  <ErrorBoundary>
    <template #default>
      <SmartTable
        :data="classes"
        :columns="classColumns"
        @save="save"
        @cancel="cancel"
        @auto-save="autoSave"
      >
        <template #operation="{ row }">
          <ActionButtons
            :rowId="row.id"
            :role="row.role"
            @detail="handleOpenEditForm(row)"
            @delete="removeUser(row)"
          />
        </template>

        <template #subjectSlot="{ row, field }">
          <span>No subjects assigned</span>
        </template>
      </SmartTable>
    </template>
  </ErrorBoundary>
</template>
