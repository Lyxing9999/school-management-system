<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";

import { teacherService } from "~/api/teacher";
import type { TeacherScheduleListDTO } from "~/api/teacher/dto";
import BaseButton from "~/components/Base/BaseButton.vue";

definePageMeta({
  layout: "teacher",
});

const teacherApi = teacherService();

/* ---------------- state ---------------- */

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const schedule = ref<TeacherScheduleListDTO[]>([]);

/* ---------------- helpers ---------------- */

const weekdayShortLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

const scheduleWithDayLabel = computed(() =>
  schedule.value.map((item) => ({
    ...item,
    day_label: weekdayShortLabels[(item.day_of_week ?? 1) - 1] ?? "Unknown",
  }))
);

const totalLessons = computed(() => schedule.value.length);
const totalDistinctClasses = computed(
  () => new Set(schedule.value.map((s) => s.class_id)).size
);

const fetchSchedule = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    // Most of your APIs return { items: [...] }, so normalize here
    const res = await teacherApi.teacher.listMySchedule({ showError: false });
    const items = Array.isArray(res) ? res : (res as any)?.items ?? [];

    schedule.value = items as TeacherScheduleListDTO[];

    if (!items.length) {
      ElMessage.info("No schedule entries yet.");
    }
  } catch (error: any) {
    console.error("Failed to fetch schedule:", error);
    errorMessage.value = error?.message ?? "Failed to load schedule.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSchedule();
});
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Header -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-[var(--color-primary-light-9)] to-[var(--color-primary-light-7)] rounded-2xl border border-[color:var(--color-primary-light-5)] shadow-sm p-5"
    >
      <div>
        <h1
          class="text-2xl font-bold flex items-center gap-2 text-[color:var(--color-dark)]"
        >
          Teacher Schedule
        </h1>
        <p class="mt-1.5 text-sm text-[color:var(--color-primary-light-1)]">
          Overview of your weekly teaching schedule including classes, times and
          rooms.
        </p>
      </div>

      <BaseButton
        plain
        :loading="loading"
        class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
        @click="fetchSchedule"
      >
        Refresh
      </BaseButton>
    </div>

    <!-- Error -->
    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="rounded-xl border border-red-200/50 shadow-sm"
        @close="errorMessage = null"
      />
    </transition>

    <!-- Summary cards -->
    <el-row :gutter="16">
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover" class="stat-card">
          <div class="text-xs text-gray-500">Total lessons</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalLessons }}
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover" class="stat-card">
          <div class="text-xs text-gray-500">Distinct classes</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalDistinctClasses }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Table -->
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

      <el-table
        :data="scheduleWithDayLabel"
        v-loading="loading"
        style="width: 100%"
        size="small"
        border
        highlight-current-row
        :header-cell-style="{
          background: '#f9fafb',
          color: '#374151',
          fontWeight: '600',
          fontSize: '13px',
        }"
      >
        <el-table-column type="index" label="#" width="60" align="center" />

        <el-table-column
          prop="class_name"
          label="Class"
          min-width="180"
          show-overflow-tooltip
        />

        <el-table-column
          prop="day_label"
          label="Day"
          width="120"
          align="center"
        />

        <el-table-column label="Time" min-width="160" align="center">
          <template #default="{ row }">
            <span class="font-mono text-xs">
              {{ row.start_time }} – {{ row.end_time }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="room" label="Room" width="120" align="center" />

        <el-table-column
          prop="teacher_name"
          label="Teacher"
          min-width="160"
          show-overflow-tooltip
        />
      </el-table>

      <div
        v-if="!loading && !schedule.length"
        class="text-center text-gray-500 mt-4 text-sm"
      >
        You do not have any scheduled lessons yet.
      </div>
    </el-card>
  </div>
</template>
