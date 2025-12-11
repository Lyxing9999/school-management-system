<script setup lang="ts">
definePageMeta({
  layout: "student",
});

import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";

import { studentService } from "~/api/student";
import type { ScheduleDTO } from "~/api/types/school.dto";
import type { StudentScheduleFilterDTO } from "~/api/student/student.dto";

import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import ErrorBoundary from "~/components/Error/ErrorBoundary.vue";
import { useHeaderState } from "~/composables/useHeaderState";
const student = studentService();

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const schedule = ref<ScheduleDTO[]>([]);

/* ---------------- load schedule ---------------- */

const loadSchedule = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const params: StudentScheduleFilterDTO = {};
    const res = await student.student.getMySchedule(params);
    // API shape: { items: ScheduleDTO[] }
    schedule.value = res.items ?? [];
  } catch (err: any) {
  } finally {
    loading.value = false;
  }
};

/* ---------------- helpers ---------------- */

const dayOfWeekLabel = (d: number | string) => {
  const map: Record<string, string> = {
    "1": "Mon",
    "2": "Tue",
    "3": "Wed",
    "4": "Thu",
    "5": "Fri",
    "6": "Sat",
    "7": "Sun",
  };
  return map[String(d)] ?? String(d);
};

/* ---------------- overview stats ---------------- */

const totalLessons = computed(() => schedule.value.length);

const distinctClasses = computed(
  () => new Set(schedule.value.map((s) => s.class_id)).size
);

const { headerState } = useHeaderState({
  items: [
    {
      key: "lessons",
      getValue: () => totalLessons.value,
      singular: "lesson",
      plural: "lessons",
      suffix: "in total",
      variant: "primary",
      hideWhenZero: false,
    },
    {
      key: "classes",
      getValue: () => distinctClasses.value,
      singular: "class",
      plural: "classes",
      suffix: "distinct",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: false,
    },
  ],
});

const handleRefresh = async () => {
  if (loading.value) return;
  await loadSchedule();
};

onMounted(loadSchedule);
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- OVERVIEW HEADER -->
    <OverviewHeader
      title="My Schedule"
      description="All your lessons and timings."
      :loading="loading"
      :showRefresh="true"
      :stats="headerState"
      @refresh="handleRefresh"
    />

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
    <el-card shadow="hover">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-semibold">Weekly schedule</span>
          <span class="text-xs text-gray-500">
            {{ totalLessons }} lesson{{ totalLessons === 1 ? "" : "s" }} in
            total
          </span>
        </div>
      </template>

      <ErrorBoundary>
        <el-table
          :data="schedule"
          v-loading="loading"
          border
          size="small"
          style="width: 100%"
          highlight-current-row
          :header-cell-style="{
            background: '#f9fafb',
            color: '#374151',
            fontWeight: '600',
            fontSize: '13px',
          }"
        >
          <el-table-column prop="day_of_week" label="Day" min-width="90">
            <template #default="{ row }">
              {{ dayOfWeekLabel(row.day_of_week) }}
            </template>
          </el-table-column>

          <el-table-column prop="start_time" label="Start" min-width="90" />
          <el-table-column prop="end_time" label="End" min-width="90" />
          <el-table-column
            prop="class_name"
            label="Class"
            min-width="200"
            show-overflow-tooltip
          />
          <el-table-column
            prop="teacher_name"
            label="Teacher"
            min-width="200"
            show-overflow-tooltip
          />
          <el-table-column prop="room" label="Room" min-width="100" />
        </el-table>

        <!-- EMPTY STATE -->
        <div
          v-if="!loading && !schedule.length"
          class="text-center text-gray-500 text-sm py-4"
        >
          No schedule data yet.
        </div>
      </ErrorBoundary>
    </el-card>
  </div>
</template>

<style scoped></style>
