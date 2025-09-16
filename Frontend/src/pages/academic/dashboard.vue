<script setup lang="ts">
definePageMeta({
  layout: "academic",
});
import { AcademicApi } from "~/api/academic/academic.api";
import type { AxiosInstance } from "axios";
import { AcademicService } from "~/services/academicService";
import { useNuxtApp } from "nuxt/app";
import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import type { AcademicFindClassDTO } from "~/api/academic/academic.dto";
const $api = useNuxtApp().$api as AxiosInstance;
const academicService = new AcademicService(
  new AcademicApi($api as AxiosInstance)
);

const classes = ref([]);
const fetch = () => {
  academicService.getClasses().then((res) => {
    classes.value = res;
    console.log(classes.value);
  });
};
import { ElInput, ElSwitch, ElButton, ElInputNumber } from "element-plus";
import { Edit } from "@element-plus/icons-vue";

const dataColumns = [
  {
    label: "ID",
    field: "id",
    component: ElInput,
    componentProps: {
      readonly: true,
    },
  },
  {
    label: "Name",
    field: "name",
    width: "120px",
    controls: false,
    autoSave: true,
    component: ElInput,
  },
  {
    label: "Grade",
    field: "grade",
    controls: false,
    autoSave: true,
    width: "150px",
    component: ElInputNumber,
    componentProps: {
      style: "width: 100%; text-align: center",
      min: 0,
      max: 12,
    },
  },
  {
    label: "Max Students",
    field: "max_students",
    width: "150px",
    autoSave: true,
    controls: false,
    component: ElInputNumber,
    componentProps: {
      style: "width: 100%; text-align: center",
      min: 0,
      max: 100,
    },
  },
  {
    label: "Teacher",
    field: "teacher",
    inlineEditActive: true,
    component: ElInput,
    componentProps: {
      readonly: true,
    },
  },
  {
    label: "Students",
    field: "students",
    inlineEditActive: true,
    component: ElInput,
    componentProps: {
      readonly: true,
    },
    formatter: (row: any) => {
      return row.students?.length ? row.students.join(", ") : "-";
    },
  },
  {
    label: "Status",
    field: "status",
    inlineEditActive: true,
    component: ElSwitch,
    componentProps: {
      activeValue: true,
      inactiveValue: false,
    },
  },
  {
    label: "Action",
    field: "action",
    component: ElButton,
    componentProps: {
      type: "primary",
      icon: Edit,
      size: "small",
      onClick: (row: any) => {
        console.log("Edit clicked for:", row.id);
        // Call your edit handler here
      },
    },
  },
];

onMounted(() => {
  fetch();
});
</script>

<template>
  <SmartTable :data="classes" :columns="dataColumns" @save="save" />
</template>
