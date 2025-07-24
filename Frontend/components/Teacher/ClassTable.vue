<template>
  <el-table :data="classes" style="width: 100%">
    <el-table-column prop="class_info.course_code" label="Code" width="150" />
    <el-table-column
      prop="class_info.course_title"
      label="Title"
      min-width="150"
    />
    <el-table-column prop="class_info.lecturer" label="Lecturer" width="160" />

    <el-table-column label="Schedule" min-width="200">
      <template #default="{ row }">
        <div v-for="(s, idx) in row.class_info.schedule" :key="idx">
          {{ s.day }}: {{ s.start_time }} - {{ s.end_time }} ({{ s.location }})
        </div>
      </template>
    </el-table-column>
    <el-table-column label="Actions" width="160">
      <template #default="{ row }">
        <el-button size="small" type="primary" @click="view(row)"
          >View</el-button
        >
        <el-button size="small" type="danger" @click="remove(row._id)"
          >Delete</el-button
        >
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
const props = defineProps<{
  classes: any[];
}>();

const emit = defineEmits<{
  (e: "view", row: any): void;
  (e: "delete", id: string): void;
}>();

const view = (row: any) => emit("view", row);
const remove = (id: string) => emit("delete", id);
</script>
