<script setup lang="ts">
definePageMeta({
  layout: "student",
});

import { ref, onMounted, computed } from "vue";

import { studentService } from "~/api/student";
import type { StudentClassListDTO } from "~/api/student/student.dto";
import { formatDate } from "~/utils/formatDate";

import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import { useHeaderState } from "~/composables/useHeaderState";
const student = studentService();

/**
 * DTO shape:
 * - StudentClassListDTO: { items: ClassItem[] }
 */
type StudentClassItem = StudentClassListDTO["items"][number];

const loading = ref(false);
const classes = ref<StudentClassItem[]>([]);

/* ---------------- load classes ---------------- */

const loadClasses = async () => {
  loading.value = true;
  try {
    // Let service handle error messages
    const res = await student.student.getMyClasses({
      showError: true,
    });
    classes.value = res.items ?? [];
  } finally {
    loading.value = false;
  }
};

onMounted(loadClasses);
/* ---------------- basic numbers ---------------- */

const totalClasses = computed(() => classes.value.length);

const totalSubjects = computed(() =>
  classes.value.reduce((sum, c) => {
    const count =
      // backend-enriched value if available
      (c as any).subject_count ??
      // fallback to raw subject_ids length
      c.subject_ids?.length ??
      0;
    return sum + (count || 0);
  }, 0)
);

/* ---------------- overview stats ---------------- */

const { headerState } = useHeaderState({
  items: [
    {
      key: "classes",
      getValue: () => totalClasses.value,
      singular: "class",
      plural: "classes",
      variant: "primary",
      hideWhenZero: true,
    },
    {
      key: "subjects",
      getValue: () => totalSubjects.value,
      singular: "subject",
      plural: "subjects",
      suffix: "in total",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});

const headerDescription = computed(() => {
  const count = totalClasses.value;
  if (!count) {
    return "You are not enrolled in any classes yet.";
  }
  if (count === 1) {
    return "You are enrolled in 1 class.";
  }
  return `You are enrolled in ${count} classes.`;
});
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- OVERVIEW HEADER -->
    <OverviewHeader
      title="My Classes"
      :description="headerDescription"
      :loading="loading"
      :showRefresh="true"
      :stats="headerState"
      @refresh="loadClasses"
    >
      <!-- Filters slot (you can extend later if needed) -->
      <template #filters>
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2 text-xs text-gray-500">
            This page shows all classes you are currently enrolled in.
          </div>
        </div>
      </template>
    </OverviewHeader>

    <!-- TABLE CARD -->
    <el-card shadow="hover">
      <el-table
        :data="classes"
        v-loading="loading"
        style="width: 100%"
        highlight-current-row
        border
        size="small"
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

        <!-- Subject count -->
        <el-table-column label="Subjects #" min-width="110" align="center">
          <template #default="{ row }">
            {{ row.subject_count ?? row.subject_ids?.length ?? 0 }}
          </template>
        </el-table-column>

        <!-- Student count -->
        <el-table-column label="Students" min-width="140" align="center">
          <template #default="{ row }">
            <span>
              {{ row.student_count ?? row.student_ids?.length ?? 0 }}
              /
              {{ row.max_students ?? "∞" }}
            </span>
          </template>
        </el-table-column>

        <!-- Created at -->
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

      <!-- Empty state -->
      <div
        v-if="!loading && !classes.length"
        class="text-center text-gray-500 mt-4 text-sm"
      >
        You are not enrolled in any classes yet.
      </div>
    </el-card>
  </div>
</template>

<style scoped></style>
