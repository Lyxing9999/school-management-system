<script lang="ts" setup>
definePageMeta({
  layout: "academic",
});
import { AcademicApi } from "~/api/academic/academic.api";
import { useNuxtApp } from "nuxt/app";
import { AcademicService } from "~/services/academicService";
import { usePaginatedFetch } from "~/composables/pagination/usePaginatedFetch";
import { useInlineEdit } from "~/composables/inline-edit/useInlineEdit";
import Pagination from "~/components/TableEdit/Pagination/Pagination.vue";
import type { AcademicGetStudentsPayload } from "~/api/academic/academic.dto";
import ActionButtons from "~/components/Button/ActionButtons.vue";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";

import type { AxiosInstance } from "axios";
const $api = useNuxtApp().$api as AxiosInstance;

const academicApi = new AcademicApi($api);
const dummyMode = ref(undefined);
const academicService = new AcademicService(academicApi);
const {
  loading: fetchLoading,
  fetchPage,
  goPage,
  currentPage,
  pageSize,
  totalRows,
} = usePaginatedFetch(
  async (_roles, page, pageSize) => {
    const res = await academicService.getStudents(page, pageSize);
    setData(res?.students ?? []);
    return { items: res?.students ?? [], total: res?.total ?? 0 };
  },
  1,
  15,
  dummyMode
);
const { data, setData } = useInlineEdit<AcademicGetStudentData>([], {
  update: (id, payload) => academicService.updateStudent(id, payload as any),
  remove: async (id) => {
    await academicService.deleteStudent(id);
  },
});
onMounted(() => {
  fetchPage();
});

import { userColumns } from "~/schemas/columns/admin/userColumns";
const academicColumns = userColumns.filter((col) => col.field !== "operation");
const deleteStudent = (id: string) => {
  academicService.deleteStudent(id);
};
</script>
<template>
  <ElCard>
    <SmartTable
      :loading="fetchLoading"
      :data="data"
      :columns="academicColumns"
      :page="currentPage"
      :page-size="pageSize"
      :total-rows="totalRows"
      @go-page="goPage"
      @fetch-page="fetchPage"
    />
  </ElCard>
  <Pagination
    :current-page="currentPage"
    :page-size="pageSize"
    :total="totalRows"
    @go-page="goPage"
  />
</template>
