<!-- ~/pages/student/classes/index.vue -->
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { studentService } from "~/api/student";
import type { ClassSectionDTO } from "~/api/types/school.dto";

definePageMeta({
  layout: "student", // or "default", depending on your app
});

const router = useRouter();
const student = studentService();

const loading = ref(false);
const classes = ref<ClassSectionDTO[]>([]);
const errorMessage = ref<string | null>(null);

const loadClasses = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await student.student.getMyClasses();
    classes.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load classes.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

onMounted(loadClasses);
</script>

<template>
  <div class="p-4 space-y-4">
    <el-row justify="space-between" align="middle">
      <el-col :span="12">
        <h1 class="text-xl font-semibold">My Classes</h1>
      </el-col>
      <el-col :span="12" class="text-right">
        <el-button type="primary" :loading="loading" @click="loadClasses">
          Refresh
        </el-button>
      </el-col>
    </el-row>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mb-2"
    />

    <el-card shadow="hover">
      <el-table
        :data="classes"
        v-loading="loading"
        style="width: 100%"
        highlight-current-row
      >
        <el-table-column prop="name" label="Class Name" min-width="180" />
        <el-table-column
          label="# Subjects"
          min-width="120"
          :formatter="(row) => row.subject_ids?.length ?? 0"
        />
        <el-table-column
          label="# Students"
          min-width="120"
          :formatter="(row) => row.student_ids?.length ?? 0"
        />
        <el-table-column
          prop="name"
          label="Class name"
          min-width="260"
          show-overflow-tooltip
        />
      </el-table>

      <div
        v-if="!loading && !classes.length"
        class="text-center text-gray-500 mt-4"
      >
        You are not enrolled in any classes yet.
      </div>
    </el-card>
  </div>
</template>
