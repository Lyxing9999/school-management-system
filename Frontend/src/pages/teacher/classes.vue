<!-- ~/pages/teacher/classes/index.vue -->
<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";

definePageMeta({
  layout: "teacher",
});

const router = useRouter();
const teacher = teacherService();

const loading = ref(false);
const classes = ref<ClassSectionDTO[]>([]);
const errorMessage = ref<string | null>(null);

// summary stats
const totalClasses = computed(() => classes.value.length);
const totalStudents = computed(() =>
  classes.value.reduce((sum, c) => sum + (c.student_ids?.length ?? 0), 0)
);
const totalSubjects = computed(() =>
  classes.value.reduce((sum, c) => sum + (c.subject_ids?.length ?? 0), 0)
);

// add derived counts for table display
const displayClasses = computed(() =>
  classes.value.map((c) => ({
    ...c,
    studentCount: c.student_ids?.length ?? 0,
    subjectCount: c.subject_ids?.length ?? 0,
  }))
);

const loadClasses = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await teacher.teacher.listMyClasses(); // TeacherClassListDTO
    classes.value = res.items ?? [];

    if (!classes.value.length) {
      ElMessage.info("You don't have any classes yet.");
    }
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load classes.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

const handleRowClick = (
  row: ClassSectionDTO & { studentCount?: number; subjectCount?: number }
) => {
  if (!row.id) return;
  router.push(`/teacher/classes/${row.id}`);
};

onMounted(loadClasses);
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Header -->
    <el-row justify="space-between" align="middle" class="mb-2">
      <el-col :span="12">
        <h1 class="text-xl font-semibold">My Classes</h1>
        <p class="text-xs text-gray-500">
          Overview of the classes you are responsible for.
        </p>
      </el-col>
      <el-col :span="12" class="text-right">
        <el-button type="primary" :loading="loading" @click="loadClasses">
          Refresh
        </el-button>
      </el-col>
    </el-row>

    <!-- Error -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mb-2"
    />

    <!-- Summary cards -->
    <el-row :gutter="16" class="mb-2">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500">Total classes</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalClasses }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500">Total students (all classes)</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalStudents }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="8">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500">Total subjects (all classes)</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalSubjects }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Main table -->
    <el-card shadow="hover">
      <el-table
        :data="displayClasses"
        v-loading="loading"
        style="width: 100%"
        highlight-current-row
        @row-click="handleRowClick"
      >
        <el-table-column prop="name" label="Class Name" min-width="180" />

        <el-table-column label="Teacher" min-width="160">
          <template #default="{ row }">
            <!-- If you later add teacher_name to DTO, it will show automatically -->
            <span>{{ row.teacher_name || "Me" }}</span>
          </template>
        </el-table-column>

        <el-table-column label="Subjects" min-width="120">
          <template #default="{ row }">
            <span>{{ row.subjectCount }}</span>
          </template>
        </el-table-column>

        <el-table-column label="# Students" min-width="120">
          <template #default="{ row }">
            <span>{{ row.studentCount }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="id"
          label="Class ID"
          min-width="260"
          show-overflow-tooltip
        />
      </el-table>

      <div
        v-if="!loading && !classes.length"
        class="text-center text-gray-500 mt-4 text-sm"
      >
        You don't have any classes yet.
      </div>
    </el-card>
  </div>
</template>
