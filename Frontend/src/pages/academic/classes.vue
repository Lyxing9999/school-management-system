<script setup lang="ts">
definePageMeta({
  layout: "academic",
});
import { classColumns } from "~/schemas/columns/academic/classColumns";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import type { AcademicBaseClassDataDTO } from "~/api/academic/academic.dto";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import {
  useClassFormSchema,
  initialClassData,
} from "~/schemas/forms/academic/classForm";
import ActionButtons from "~/components/Button/ActionButtons.vue";

const classes = ref<AcademicBaseClassDataDTO[]>([]);

const { $academicService } = useNuxtApp();
const serviceWrapper = {
  create: async (payload: AcademicBaseClassDataDTO) =>
    await $academicService.createClass(payload),
};
function fetchClasses() {
  $academicService.getClasses().then((data: AcademicBaseClassDataDTO[]) => {
    classes.value = data ?? [];
  });
}

onMounted(async () => {
  fetchClasses();
});
const {
  formDialogVisible,
  formData,
  loading,
  openForm,
  saveForm,
  cancelForm,
  deleteItem,
} = useFormDetail<AcademicBaseClassDataDTO>(serviceWrapper, initialClassData, {
  notify: (msg, type) => console.log(type, msg),
  enableDelete: true,
  onSuccess: () => fetchClasses(),
  onError: (err) => console.error(err),
});
const openFormDialog = () => {
  openForm();
};
const classFormSchema = useClassFormSchema();
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
