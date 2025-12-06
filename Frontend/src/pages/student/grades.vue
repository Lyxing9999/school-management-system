<!-- ~/pages/student/grades/index.vue -->
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";

import { studentService } from "~/api/student";
import type { GradeDTO } from "~/api/types/school.dto";
import type { StudentGradesFilterDTO } from "~/api/student/student.dto";

import { formatDate } from "~/utils/formatDate";

definePageMeta({
  layout: "student",
});

const student = studentService();

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const grades = ref<GradeDTO[]>([]);
const termFilter = ref<string>("");

const loadGrades = async () => {
  loading.value = true;
  errorMessage.value = null;
  try {
    const params: StudentGradesFilterDTO = {};
    if (termFilter.value.trim()) {
      params.term = termFilter.value.trim();
    }
    const res = await student.student.getMyGrades(params);
    grades.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load grades.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};
onMounted(loadGrades);

const formatType = (value?: string) => {
  if (!value) return "";
  return value.charAt(0).toUpperCase() + value.slice(1);
};
</script>

<template>
  <div class="p-4 space-y-4">
    <el-row justify="space-between" align="middle">
      <el-col :span="18">
        <h1 class="text-xl font-semibold">My Grades</h1>
        <p class="text-xs text-gray-500">
          View your grades across subjects and terms.
        </p>
      </el-col>
      <el-col :span="6" class="text-right">
        <el-button type="primary" :loading="loading" @click="loadGrades">
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

    <el-card shadow="hover" class="space-y-4">
      <!-- Filters -->
      <el-form inline label-width="60px" size="small">
        <el-form-item label="Term">
          <el-input
            v-model="termFilter"
            placeholder="e.g. 2025-S1"
            style="min-width: 200px"
            clearable
            @keyup.enter="loadGrades"
          />
        </el-form-item>
        <el-form-item>
          <el-button size="small" type="primary" @click="loadGrades">
            Apply
          </el-button>
        </el-form-item>
      </el-form>

      <!-- Grades table -->
      <el-table
        :data="grades"
        v-loading="loading"
        border
        size="small"
        style="width: 100%"
      >
        <!-- Subject label from backend -->
        <el-table-column
          prop="subject_label"
          label="Subject"
          min-width="200"
          show-overflow-tooltip
        />

        <!-- Class name, not class_id -->
        <el-table-column
          prop="class_name"
          label="Class"
          min-width="180"
          show-overflow-tooltip
        />

        <!-- Score -->
        <el-table-column
          prop="score"
          label="Score"
          min-width="80"
          align="right"
        />

        <!-- Type as small tag -->
        <el-table-column label="Type" min-width="110">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">
              {{ formatType(row.type) }}
            </el-tag>
          </template>
        </el-table-column>

        <!-- Term -->
        <el-table-column
          prop="term"
          label="Term"
          min-width="120"
          show-overflow-tooltip
        />

        <!-- Created date (nice format) -->
        <el-table-column label="Recorded At" min-width="140">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <!-- Low-priority raw record id (optional) -->
        <el-table-column
          prop="id"
          label="Record ID"
          min-width="220"
          show-overflow-tooltip
        />
      </el-table>

      <div
        v-if="!loading && !grades.length"
        class="text-center text-gray-500 text-sm py-4"
      >
        No grades found for this filter.
      </div>
    </el-card>
  </div>
</template>
