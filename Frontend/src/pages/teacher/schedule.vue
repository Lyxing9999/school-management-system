<!-- ~/pages/teacher/schedule/index.vue -->
<script setup lang="ts">
definePageMeta({
  layout: "teacher",
});

import { ref, computed, onMounted } from "vue";

import { teacherService } from "~/api/teacher";
import type { TeacherScheduleListDTO } from "~/api/teacher/dto";

import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import ErrorBoundary from "~/components/Error/ErrorBoundary.vue";
import { usePaginatedFetch } from "~/composables/usePaginatedFetch";
import { useHeaderState } from "~/composables/useHeaderState";

const teacherApi = teacherService();

/**
 * In your DTOs you used `TeacherScheduleListDTO` as the item type
 * (same as on the teacher dashboard).
 */
type TeacherScheduleItem = TeacherScheduleListDTO & {
  day_label?: string;
};

/* --------------------------------
 * Pagination + data (usePaginatedFetch)
 * -------------------------------- */

// dummy filter ref (no filter, just pagination)
const dummyFilter = ref<null>(null);

const weekdayShortLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

const {
  data: schedule, // current page items
  loading,
  error,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<TeacherScheduleItem, null>(
  async (_unused, page, pageSize, signal) => {
    const res = await teacherApi.teacher.listMySchedule({
      page,
      page_size: pageSize,
      signal,
      showError: false,
    });

    // Normalize: array or { items, total }
    const rawItems = Array.isArray(res) ? res : (res as any)?.items ?? [];

    const allItems = rawItems as TeacherScheduleItem[];
    const total = (res as any)?.total ?? allItems.length;

    // Enrich with day_label
    const enrichedAll = allItems.map((item) => ({
      ...item,
      day_label: weekdayShortLabels[(item.day_of_week ?? 1) - 1] ?? "Unknown",
    }));

    // Fake frontend pagination (until backend supports page/page_size)
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const pageItems = enrichedAll.slice(start, end);

    return {
      items: pageItems,
      total,
    };
  },
  1,
  10,
  dummyFilter
);

/* --------------------------------
 * Error mapping
 * -------------------------------- */

const errorMessage = computed<string | null>(() =>
  error.value ? error.value.message ?? "Failed to load schedule." : null
);

/* --------------------------------
 * Stats for header (using useHeaderState)
 * -------------------------------- */

const totalLessons = computed(() => totalRows.value ?? 0);

// Distinct classes only on the current page
const totalDistinctClassesOnPage = computed(() => {
  const items = schedule.value ?? [];
  return new Set(items.map((s) => s.class_id)).size;
});

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
      key: "classes_page",
      getValue: () => totalDistinctClassesOnPage.value,
      singular: "class",
      plural: "classes",
      suffix: "on this page",
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: false,
    },
  ],
});

/* --------------------------------
 * Fetch + pagination handlers
 * -------------------------------- */

const fetchSchedule = async () => {
  await fetchPage(currentPage.value || 1);
};

onMounted(async () => {
  await fetchSchedule();
});

const handlePageChange = (page: number) => {
  goPage(page);
};

const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  fetchPage(1);
};
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- OVERVIEW HEADER -->
    <OverviewHeader
      title="Teacher Schedule"
      description="Overview of your weekly teaching schedule including classes, times and rooms."
      :showRefresh="true"
      :loading="loading"
      :stats="headerState"
      @refresh="fetchSchedule"
    />

    <!-- ERROR BANNER -->
    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="rounded-xl border border-red-200/50 shadow-sm"
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

          <el-table-column
            prop="room"
            label="Room"
            width="120"
            align="center"
          />

          <el-table-column
            prop="teacher_name"
            label="Teacher"
            min-width="160"
            show-overflow-tooltip
          />
        </el-table>

        <!-- PAGINATION -->
        <div v-if="totalLessons > 0" class="mt-4 flex justify-end">
          <el-pagination
            background
            layout="prev, pager, next, jumper, sizes, total"
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalLessons"
            @current-change="handlePageChange"
            @size-change="handlePageSizeChange"
          />
        </div>

        <!-- EMPTY STATE -->
        <div
          v-if="!loading && !schedule?.length"
          class="text-center text-gray-500 mt-4 text-sm"
        >
          You do not have any scheduled lessons yet.
        </div>
      </ErrorBoundary>
    </el-card>
  </div>
</template>

<style scoped></style>
