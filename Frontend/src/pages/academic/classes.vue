<script setup lang="ts">
definePageMeta({
  layout: "academic",
});
import { classColumns } from "~/schemas/columns/academic/classColumns";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import type { AcademicGetClassData } from "~/api/academic/academic.dto";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import ActionButtons from "~/components/Button/ActionButtons.vue";

import { useDynamicCreateFormReactive } from "~/schemas/registry/academic/AcademicFormDynamic";
const classes = ref<AcademicGetClassData[]>([]);

const selectedFormCreate = ref<CreateMode>("CLASS");
function fetchClasses() {
  $academicService.getClasses().then((data: AcademicGetClassData[]) => {
    classes.value = data ?? [];
  });
}

onMounted(async () => {
  fetchClasses();
});
const {
  formDialogVisible,
  schema: classFormSchema,
  formData,
  loading,
  openForm,
  saveForm,
  cancelForm,
} = useDynamicCreateFormReactive(selectedFormCreate);
const openFormDialog = () => {
  openForm();
};
</script>

<template>
  <BaseButton type="primary" @click="openFormDialog">Create Class</BaseButton>

  <SmartFormDialog
    v-model:visible="formDialogVisible"
    v-model="formData"
    :fields="classFormSchema"
    title="Create Class"
    :loading="loading"
    @save="saveForm"
    @cancel="cancelForm"
  />

  <SmartTable
    :data="classes"
    highlight-current-row
    :columns="classColumns"
    :smart-props="{
      rowKey: 'id',
      border: true,
      stripe: true,
    }"
  >
    <template #operation="{ row }">
      <ActionButtons
        :rowId="row.id"
        :hide-detail-for-roles="['admin']"
        content="View Details"
        :onDelete="() => deleteItem(row.id)"
      />
    </template>
  </SmartTable>
</template>

<style scoped></style>
