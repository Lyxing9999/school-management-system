<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import { teacherService } from "~/api/teacher";
import type { ClassSectionDTO } from "~/api/types/school.dto";

definePageMeta({
  layout: "teacher",
});

const teacher = teacherService();

const loading = ref(false);
const classes = ref<ClassSectionDTO[]>([]);
const errorMessage = ref<string | null>(null);

const totalClasses = computed(() => classes.value.length);
const totalStudents = computed(() =>
  classes.value.reduce((sum, c) => sum + (c.student_ids?.length ?? 0), 0)
);

const loadData = async () => {
  loading.value = true;
  errorMessage.value = null;
  try {
    const res = await teacher.teacher.listMyClasses();
    classes.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load dashboard data.";
    ElMessage.error(errorMessage.value ?? "Failed to load dashboard data.");
  } finally {
    loading.value = false;
  }
};

onMounted(loadData);
</script>

<template>
  <div class="p-4 space-y-4">
    <el-row justify="space-between" align="middle">
      <el-col :span="18">
        <h1 class="text-xl font-semibold">Teacher Dashboard</h1>
        <p class="text-xs text-gray-500">
          Overview of your classes and students
        </p>
      </el-col>
      <el-col :span="6" class="text-right">
        <el-button type="primary" :loading="loading" @click="loadData">
          Refresh
        </el-button>
      </el-col>
    </el-row>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
    />

    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Classes</div>
          <div class="text-2xl font-semibold">{{ totalClasses }}</div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Students</div>
          <div class="text-2xl font-semibold">{{ totalStudents }}</div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Today</div>
          <div class="text-sm text-gray-600">
            Use "My Classes" to mark attendance and manage grades.
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="mt-4">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-semibold">My Classes (quick view)</span>
        </div>
      </template>

      <el-table
        :data="classes"
        v-loading="loading"
        size="small"
        style="width: 100%"
      >
        <el-table-column prop="name" label="Class" min-width="160" />
        <el-table-column
          label="Students"
          min-width="100"
          :formatter="(row) => row.student_ids?.length ?? 0"
        />
        <el-table-column
          label="Subjects"
          min-width="100"
          :formatter="(row) => row.subject_ids?.length ?? 0"
        />
        <el-table-column label="Actions" min-width="140" fixed="right">
          <template #default="{ row }">
            <NuxtLink :to="`/teacher/classes/${row.id}`">
              <el-button type="primary" size="small">Open</el-button>
            </NuxtLink>
          </template>
        </el-table-column>
      </el-table>

      <div
        v-if="!loading && !classes.length"
        class="text-center text-gray-500 py-4 text-sm"
      >
        No classes assigned yet.
      </div>
    </el-card>
  </div>
</template>
