<script setup lang="ts">
definePageMeta({
  layout: "academic",
});

import SmartTable from "~/components/TableEdit/core/SmartTable.vue";

import { ElSwitch } from "element-plus";
const columns = [
  { label: "ID", field: "id", type: "number" },
  { label: "Name", field: "name", type: "text" },
  { label: "Teacher", field: "teacher", type: "text" },
  { label: "Students", field: "students", type: "number" },
  {
    label: "Status",
    field: "status",
    width: "100px",
    fixed: true,
    inlineEditActive: true,
    component: ElSwitch,
    componentProps: {
      activeValue: "Active",
      inactiveValue: "Inactive",
    },
  },
  { label: "Action", field: "action", type: "button", buttonText: "Edit" },
];

// Fake data
const mockData = [
  {
    id: 1,
    name: "Class 1",
    teacher: "Mr. Smith",
    students: 30,
    status: "Active",
    action: "",
  },
  {
    id: 2,
    name: "Class 2",
    teacher: "Ms. Johnson",
    students: 25,
    status: "Inactive",
    action: "",
  },
  {
    id: 3,
    name: "Class 3",
    teacher: "Mr. Lee",
    students: 28,
    status: "Active",
    action: "",
  },
  {
    id: 4,
    name: "Class 4",
    teacher: "Mrs. Brown",
    students: 32,
    status: "Active",
    action: "",
  },
  {
    id: 5,
    name: "Class 5",
    teacher: "Ms. White",
    students: 20,
    status: "Inactive",
    action: "",
  },
];
import { ElInput } from "element-plus";
import { ElDatePicker } from "element-plus";
const fields = [
  {
    key: "name",
    label: "Class Name",
    component: ElInput,
    inlineEdit: true,
    componentProps: {
      class: "p-10",
    },
  },
  { key: "teacher", label: "Teacher", component: ElInput, inlineEdit: true },
  { key: "students", label: "Number of Students", component: ElInput },
  {
    key: "status",
    label: "Active",
    component: ElDatePicker,
    componentProps: { activeValue: true, inactiveValue: false },
    inlineEdit: true,
  },
];
import SmartForm from "~/components/Form/SmartForm.vue";
const formData = {
  name: "",
  teacher: "",
  students: 0,
  status: true,
};
const handleAddClass = () => {
  dialogVisible.value = true;
};
const dialogVisible = ref(false);
import BaseButton from "~/components/Base/BaseButton.vue";
</script>

<template>
  <SmartTable :columns="columns" :data="mockData" />

  <el-button @click="dialogVisible = true">Add Class</el-button>
  <el-dialog title="Edit Class" v-model="dialogVisible">
    <SmartForm
      :modelValue="formData"
      :fields="fields"
      @update:modelValue="(val) => console.log('Saved:', val)"
    >
      <template #operation="{ form }">
        <BaseButton @click="dialogVisible = false">Cancel</BaseButton>
        <BaseButton type="primary" @click="dialogVisible = false"
          >Save</BaseButton
        >
      </template>
    </SmartForm>
  </el-dialog>
</template>
