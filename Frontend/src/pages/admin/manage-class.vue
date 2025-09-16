<script lang="ts" setup>
import { ref } from "vue";
import SmartForm from "~/components/Form/SmartForm.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import { AdminService } from "~/services/adminService";
import { AdminApi } from "~/api/admin/admin.api";
import type { AdminCreateClass } from "~/api/admin/admin.dto";
import { useForm } from "~/composables/useForm";
import {
  useClassFormSchema,
  formData,
  fetchOwners,
} from "~/schemas/forms/admin/classForm";

definePageMeta({
  layout: "admin",
});

const mockData = ref([
  {
    id: 1,
    class_name: "Class 1",
    owner_class: "Class 1",
    grade: 1,
  },
  {
    id: 2,
    class_name: "Class 2",
    owner_class: "Class 2",
    grade: 2,
  },
  {
    id: 3,
    class_name: "Class 3",
    owner_class: "Class 3",
    grade: 3,
  },
]);
import type { AxiosInstance } from "axios";
const $api = useNuxtApp().$api as AxiosInstance;
const adminApi = new AdminApi($api);
const adminService = new AdminService(adminApi);
const {
  formDialogVisible,
  formData: createFormData,
  loading,
  openForm,
  saveForm,
  cancelForm,
} = useForm(
  {
    create: (data: AdminCreateClass) => adminService.createClass(data),
  },
  formData,
  {
    onError: (err: any) => console.error(err),
  }
);

onMounted(() => fetchOwners());
const classFormSchema = useClassFormSchema();
</script>

<template>
  <BaseButton type="primary" @click="openForm">Add Class</BaseButton>
  <el-dialog v-model="formDialogVisible" title="Add New Class" width="500px">
    <SmartForm
      :model-value="createFormData"
      :fields="classFormSchema"
      @save="saveForm"
      @cancel="cancelForm"
      :useElForm="true"
    />
  </el-dialog>

  <SmartTable :columns="columns" :data="mockData" />
</template>
