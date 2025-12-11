<script setup lang="ts">
definePageMeta({
  layout: "student",
});

import { ref, onMounted, computed } from "vue";

import { studentService } from "~/api/student";
import type { GradeDTO } from "~/api/types/school.dto";
import type {
  StudentGradesFilterDTO,
  StudentGradeListDTO,
} from "~/api/student/student.dto";
import { useHeaderState } from "~/composables/useHeaderState";
import { formatDate } from "~/utils/formatDate";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
const student = studentService();

/**
 * You can keep GradeDTO, but we'll also define the list item type
 * from StudentGradeListDTO in case backend adds more fields later.
 */
type StudentGradeItem = StudentGradeListDTO["items"][number];

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const grades = ref<StudentGradeItem[] | GradeDTO[]>([]);
const termFilter = ref<string>("");

/* ---------------- load grades ---------------- */

const loadGrades = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const params: StudentGradesFilterDTO = {};
    if (termFilter.value.trim()) {
      params.term = termFilter.value.trim();
    }

    const res = await student.student.getMyGrades(params);
    // API shape: { items: GradeDTO[] }
    grades.value = res.items ?? [];
  } catch (e) {
  } finally {
    loading.value = false;
  }
};

onMounted(loadGrades);

/* ---------------- helpers ---------------- */

// script
const getTagType = (value?: string) => {
  if (!value) return "primary";

  const v = value.toLowerCase();
  if (v === "assignment") return "success";
  if (v === "exam") return "danger";
  return "primary";
};

const formatType = (value?: string) => {
  if (!value) return "";
  return value.charAt(0).toUpperCase() + value.slice(1);
};
/* ---------------- overview stats ---------------- */

const totalGrades = computed(() => grades.value.length);

const distinctSubjects = computed(
  () =>
    new Set(grades.value.map((g: any) => g.subject_id || g.subject_label)).size
);

const averageScore = computed(() => {
  if (!grades.value.length) return null;

  const sum = grades.value.reduce((acc: number, g: any) => {
    const s = Number(g.score);
    return Number.isFinite(s) ? acc + s : acc;
  }, 0);

  return Math.round((sum / grades.value.length) * 10) / 10; // 1 decimal
});

const { headerState } = useHeaderState({
  items: [
    {
      key: "total",
      getValue: () => totalGrades.value,
      singular: "record",
      plural: "records",
      variant: "primary",
      hideWhenZero: true,
    },
    {
      key: "subjects",
      getValue: () => distinctSubjects.value,
      singular: "subject",
      plural: "subjects",
      suffix: "graded",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
    {
      key: "avg_score",
      getValue: () => averageScore.value ?? 0,
      label: (v) =>
        averageScore.value === null ? undefined : `Average score: ${v}`,
      variant: "secondary",
      dotClass: "bg-blue-500",
      hideWhenZero: true,
    },
  ],
});
const canRefresh = computed(() => !loading.value);

const handleRefresh = async () => {
  if (!canRefresh.value) return;
  await loadGrades();
};
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- OVERVIEW HEADER -->
    <OverviewHeader
      title="My Grades"
      description="View your grades across subjects and terms."
      :loading="loading"
      :showRefresh="true"
      :disabled="true"
      :stats="headerState"
      @refresh="handleRefresh"
    >
      <!-- Filters: term input -->
      <template #filters>
        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Term:</span>
            <el-input
              v-model="termFilter"
              placeholder="e.g. 2025-S1"
              style="min-width: 200px"
              size="small"
              clearable
              @keyup.enter="loadGrades"
            />
            <BaseButton
              size="small"
              type="primary"
              :loading="loading"
              @click="loadGrades"
            >
              Apply
            </BaseButton>
          </div>
        </div>
      </template>
    </OverviewHeader>

    <!-- ERROR -->
    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="mb-2 rounded-xl border border-red-200/60 shadow-sm"
        @close="errorMessage = null"
      />
    </transition>

    <!-- MAIN CARD -->
    <el-card shadow="hover" class="space-y-4">
      <!-- Small header inside card (optional, but consistent) -->
      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
      >
        <div>
          <div class="text-base font-semibold text-gray-800">Grade records</div>
          <p class="text-xs text-gray-500">
            Each row is one grade for a subject, class and term.
          </p>
        </div>

        <div class="text-xs text-gray-500">
          Total: {{ totalGrades }} record{{ totalGrades === 1 ? "" : "s" }}
        </div>
      </div>

        <!-- Grades table -->
        <el-table
          :data="grades"
          v-loading="loading"
          border
          size="small"
          style="width: 100%"
          highlight-current-row
        >
          <!-- Subject label from backend -->
          <el-table-column
            prop="subject_label"
            label="Subject"
            min-width="200"
            show-overflow-tooltip
          />

          <!-- Class name -->
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
              <el-tag size="small" effect="plain" :type="getTagType(row.type)">
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

          <!-- Created date -->
          <el-table-column label="Recorded At" min-width="140">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>

        <!-- Empty state -->
        <div
          v-if="!loading && !grades.length"
          class="text-center text-gray-500 text-sm py-4"
        >
          No grades found for this filter.
        </div>
    </el-card>
  </div>
</template>

<style scoped></style>
