<!-- ~/pages/teacher/classes/index.vue -->
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";
import { ElMessage } from "element-plus";

definePageMeta({
  layout: "teacher", // change to "default" / whatever layout you use
});

const router = useRouter();
const teacher = teacherService();

const loading = ref(false);
const classes = ref<ClassSectionDTO[]>([]);
const errorMessage = ref<string | null>(null);

const loadClasses = async () => {
  loading.value = true;
  errorMessage.value = null;
  try {
    const res = await teacher.teacher.getMyClasses(); // TeacherClassListDTO
    classes.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load classes.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

const handleRowClick = (row: ClassSectionDTO) => {
  router.push(`/teacher/classes/${row.id}`);
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
        @row-click="handleRowClick"
        style="width: 100%"
        highlight-current-row
      >
        <el-table-column prop="name" label="Class Name" min-width="180" />
        <el-table-column
          label="Teacher"
          min-width="160"
          :formatter="(row) => row.teacher_id || 'Unassigned'"
        />
        <el-table-column
          label="# Students"
          min-width="120"
          :formatter="(row) => row.student_ids?.length ?? 0"
        />
        <el-table-column
          label="ID"
          min-width="260"
          :formatter="(row) => row.id"
        />
      </el-table>

      <div
        v-if="!loading && !classes.length"
        class="text-center text-gray-500 mt-4"
      >
        You don't have any classes yet.
      </div>
    </el-card>
  </div>
</template>
