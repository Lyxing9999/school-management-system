<!-- ~/pages/student/classes/index.vue -->
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";

import { studentService } from "~/api/student";
import type { ClassSectionDTO } from "~/api/types/school.dto";
import { formatDate } from "~/utils/formatDate";

definePageMeta({
  layout: "student",
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

const goToClassDetail = (row: ClassSectionDTO) => {
  // Adjust route to whatever your class detail page is
  // e.g. /student/classes/[id].vue
  router.push(`/student/classes/${row.id}`);
};

onMounted(loadClasses);
</script>

<template>
  <div class="p-4 space-y-4">
    <el-row justify="space-between" align="middle">
      <el-col :span="12">
        <h1 class="text-xl font-semibold">My Classes</h1>
        <p class="text-xs text-gray-500 mt-1">
          You are enrolled in {{ classes.length }} class<span
            v-if="classes.length !== 1"
            >es</span
          >.
        </p>
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
        @row-dblclick="goToClassDetail"
      >
        <!-- Class name -->
        <el-table-column
          prop="name"
          label="Class"
          min-width="200"
          show-overflow-tooltip
        />

        <!-- Teacher -->
        <el-table-column
          prop="teacher_name"
          label="Teacher"
          min-width="160"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span>{{ row.teacher_name || "—" }}</span>
          </template>
        </el-table-column>

        <!-- Subjects as tags -->
        <el-table-column label="Subjects" min-width="260">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1">
              <el-tag
                v-for="label in row.subject_labels || []"
                :key="label"
                size="small"
                type="info"
              >
                {{ label }}
              </el-tag>
              <span
                v-if="!row.subject_labels || !row.subject_labels.length"
                class="text-xs text-gray-400"
              >
                No subjects assigned
              </span>
            </div>
          </template>
        </el-table-column>

        <!-- Counts -->
        <el-table-column label="Subjects #" min-width="110" align="center">
          <template #default="{ row }">
            {{ row.subject_count ?? row.subject_ids?.length ?? 0 }}
          </template>
        </el-table-column>

        <el-table-column label="Students" min-width="140" align="center">
          <template #default="{ row }">
            <span>
              {{ row.student_count ?? row.student_ids?.length ?? 0 }}
              /
              {{ row.max_students ?? "∞" }}
            </span>
          </template>
        </el-table-column>

        <!-- Created at (simple text; format on frontend later if you want) -->
        <el-table-column
          prop="created_at"
          label="Created"
          min-width="180"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="text-xs text-gray-500">
              {{ formatDate(row.created_at) }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div
        v-if="!loading && !classes.length"
        class="text-center text-gray-500 mt-4 text-sm"
      >
        You are not enrolled in any classes yet.
      </div>
    </el-card>
  </div>
</template>
