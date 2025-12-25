<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";

import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import { formatDate } from "~/utils/formatDate";

import type {
  AdminDashboardDTO,
  AdminDashboardFilterDTO,
} from "~/api/admin/dashboard/dashboard.dto";

definePageMeta({
  layout: "admin",
});

/* ------------------------------------------------
 * Service
 * ------------------------------------------------ */

import { adminService } from "~/api/admin";

const adminApi = adminService();

/* ------------------------------------------------
 * State
 * ------------------------------------------------ */

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const dashboard = ref<AdminDashboardDTO | null>(null);

// Filters
const filterDateRange = ref<[Date, Date] | null>(null);
const filterTerm = ref<string | "">("");

// Term options – adjust values to match GradeRecord.term
const termOptions = [
  { label: "All terms", value: "" },
  { label: "Semester 1", value: "S1" },
  { label: "Semester 2", value: "S2" },
];

/* ------------------------------------------------
 * Helpers
 * ------------------------------------------------ */

const extractErrorMessage = (err: unknown, fallback: string): string => {
  if (err instanceof Error && err.message) return err.message;
  if (typeof err === "string") return err;
  return fallback;
};

const formatDateParam = (d: Date): string => {
  // "YYYY-MM-DD" – matches your backend _parse_date_arg helper
  return d.toISOString().slice(0, 10);
};

const buildFilterPayload = (): AdminDashboardFilterDTO => {
  const filters: AdminDashboardFilterDTO = {};

  if (filterDateRange.value) {
    const [start, end] = filterDateRange.value;
    filters.date_from = formatDateParam(start);
    filters.date_to = formatDateParam(end);
  }

  if (filterTerm.value) {
    filters.term = filterTerm.value;
  }

  return filters;
};

/* ------------------------------------------------
 * Load data
 * ------------------------------------------------ */

const loadDashboard = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const filters = buildFilterPayload();

    const data = await adminApi.dashboard.getDashboardData(filters, {
      showError: true,
      loadingRef: loading,
    });

    dashboard.value = data;
  } catch (err) {
    console.error(err);
    const message = extractErrorMessage(
      err,
      "Failed to load admin dashboard data."
    );
    errorMessage.value = message;
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadDashboard();
});

/* ------------------------------------------------
 * Derived / convenience computed
 * ------------------------------------------------ */

const overview = computed(() => dashboard.value?.overview);
const attendance = computed(() => dashboard.value?.attendance);
const grades = computed(() => dashboard.value?.grades);
const schedule = computed(() => dashboard.value?.schedule);

const totalStudents = computed(() => overview.value?.total_students ?? 0);
const totalTeachers = computed(() => overview.value?.total_teachers ?? 0);
const totalClasses = computed(() => overview.value?.total_classes ?? 0);
const totalSubjects = computed(() => overview.value?.total_subjects ?? 0);
const todayLessons = computed(() => overview.value?.today_lessons ?? 0);

// Small label for "current filter"
const activeFilterLabel = computed(() => {
  const parts: string[] = [];

  if (filterDateRange.value) {
    const [start, end] = filterDateRange.value;
    parts.push(
      `Date: ${formatDate(start.toISOString())} → ${formatDate(
        end.toISOString()
      )}`
    );
  }

  if (filterTerm.value) {
    const termLabel =
      termOptions.find((t) => t.value === filterTerm.value)?.label ||
      `Term: ${filterTerm.value}`;
    parts.push(termLabel);
  }

  if (!parts.length) return "Showing all available data";

  return parts.join(" • ");
});

/* ------------------------------------------------
 * Chart options
 * ------------------------------------------------ */

/** Attendance – status summary (pie) */
const attendanceStatusOption = computed(() => {
  const data = attendance.value?.status_summary ?? [];

  if (!data.length) {
    return {
      title: { text: "No attendance data", left: "center", top: "center" },
    };
  }

  const seriesData = data.map((row) => ({
    name: row.status,
    value: row.count,
  }));

  return {
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [
      {
        name: "Attendance",
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 6,
          borderColor: "#fff",
          borderWidth: 1,
        },
        data: seriesData,
      },
    ],
  };
});

/** Attendance – daily trend (stacked line) */
const attendanceDailyTrendOption = computed(() => {
  const rows = attendance.value?.daily_trend ?? [];

  if (!rows.length) {
    return {
      title: { text: "No daily trend data", left: "center", top: "center" },
    };
  }

  const dates = rows.map((r) => r.date);
  const present = rows.map((r) => r.present);
  const absent = rows.map((r) => r.absent);
  const excused = rows.map((r) => r.excused);

  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { top: 40, left: 40, right: 16, bottom: 40 },
    xAxis: {
      type: "category",
      data: dates,
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      name: "Records",
    },
    series: [
      {
        name: "Present",
        type: "line",
        smooth: true,
        data: present,
      },
      {
        name: "Absent",
        type: "line",
        smooth: true,
        data: absent,
      },
      {
        name: "Excused",
        type: "line",
        smooth: true,
        data: excused,
      },
    ],
  };
});

/** Attendance – by class (bar) */
const attendanceByClassOption = computed(() => {
  const rows = attendance.value?.by_class ?? [];

  if (!rows.length) {
    return {
      title: {
        text: "No class-level attendance",
        left: "center",
        top: "center",
      },
    };
  }

  const labels = rows.map((r) => r.class_name || r.class_id);
  const present = rows.map((r) => r.present);
  const absent = rows.map((r) => r.absent);
  const excused = rows.map((r) => r.excused);

  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { top: 40, left: 40, right: 16, bottom: 80 },
    xAxis: {
      type: "category",
      data: labels,
      axisLabel: {
        interval: 0,
        rotate: labels.length > 4 ? 30 : 0,
        fontSize: 11,
      },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      name: "Records",
    },
    series: [
      {
        name: "Present",
        type: "bar",
        stack: "total",
        data: present,
      },
      {
        name: "Absent",
        type: "bar",
        stack: "total",
        data: absent,
      },
      {
        name: "Excused",
        type: "bar",
        stack: "total",
        data: excused,
      },
    ],
  };
});

/** Grades – avg score by subject (bar) */
const gradeAvgBySubjectOption = computed(() => {
  const rows = grades.value?.avg_score_by_subject ?? [];

  if (!rows.length) {
    return {
      title: { text: "No grade data", left: "center", top: "center" },
    };
  }

  const labels = rows.map((r) => r.subject_name || r.subject_id);
  const values = rows.map((r) => r.avg_score);

  return {
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.axisValue}<br/>Avg score: ${p.data}`;
      },
    },
    grid: { top: 40, left: 40, right: 16, bottom: 80 },
    xAxis: {
      type: "category",
      data: labels,
      axisLabel: {
        interval: 0,
        rotate: labels.length > 4 ? 30 : 0,
        fontSize: 11,
      },
    },
    yAxis: {
      type: "value",
      name: "Avg score",
      min: 0,
      max: 100,
    },
    series: [
      {
        name: "Average",
        type: "bar",
        data: values,
        barWidth: "60%",
        itemStyle: { borderRadius: [6, 6, 0, 0] },
      },
    ],
  };
});

/** Grades – distribution (bar) */
const gradeDistributionOption = computed(() => {
  const rows = grades.value?.grade_distribution ?? [];

  if (!rows.length) {
    return {
      title: { text: "No grade distribution", left: "center", top: "center" },
    };
  }

  const labels = rows.map((r) => r.range);
  const counts = rows.map((r) => r.count);

  return {
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.axisValue}<br/>Students: ${p.data}`;
      },
    },
    grid: { top: 40, left: 40, right: 16, bottom: 40 },
    xAxis: {
      type: "category",
      data: labels,
    },
    yAxis: {
      type: "value",
      name: "Students",
      minInterval: 1,
    },
    series: [
      {
        name: "Students",
        type: "bar",
        data: counts,
        barWidth: "50%",
        itemStyle: { borderRadius: [6, 6, 0, 0] },
      },
    ],
  };
});

/** Grades – pass rate by class (bar, percentage) */
const passRateByClassOption = computed(() => {
  const rows = grades.value?.pass_rate_by_class ?? [];

  if (!rows.length) {
    return {
      title: { text: "No pass-rate data", left: "center", top: "center" },
    };
  }

  const labels = rows.map((r) => r.class_name || r.class_id);
  const rates = rows.map((r) => Number((r.pass_rate * 100).toFixed(1))); // to percentage

  return {
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.axisValue}<br/>Pass rate: ${p.data}%`;
      },
    },
    grid: { top: 40, left: 40, right: 16, bottom: 80 },
    xAxis: {
      type: "category",
      data: labels,
      axisLabel: {
        interval: 0,
        rotate: labels.length > 4 ? 30 : 0,
        fontSize: 11,
      },
    },
    yAxis: {
      type: "value",
      name: "Pass rate (%)",
      min: 0,
      max: 100,
    },
    series: [
      {
        name: "Pass rate",
        type: "bar",
        data: rates,
        barWidth: "60%",
        itemStyle: { borderRadius: [6, 6, 0, 0] },
      },
    ],
  };
});

/** Schedule – lessons by weekday */
const scheduleByWeekdayOption = computed(() => {
  const rows = schedule.value?.lessons_by_weekday ?? [];

  if (!rows.length) {
    return {
      title: { text: "No schedule data", left: "center", top: "center" },
    };
  }

  const labels = rows.map((r) => r.label);
  const lessons = rows.map((r) => r.lessons);

  return {
    tooltip: { trigger: "axis" },
    grid: { top: 40, left: 40, right: 16, bottom: 40 },
    xAxis: {
      type: "category",
      data: labels,
    },
    yAxis: {
      type: "value",
      name: "Lessons",
      minInterval: 1,
    },
    series: [
      {
        name: "Lessons",
        type: "bar",
        data: lessons,
        barWidth: "50%",
        itemStyle: { borderRadius: [6, 6, 0, 0] },
      },
    ],
  };
});

/** Schedule – lessons by teacher */
const scheduleByTeacherOption = computed(() => {
  const rows = schedule.value?.lessons_by_teacher ?? [];

  if (!rows.length) {
    return {
      title: {
        text: "No teacher schedule data",
        left: "center",
        top: "center",
      },
    };
  }

  const labels = rows.map((r) => r.teacher_name || r.teacher_id);
  const lessons = rows.map((r) => r.lessons);

  return {
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.axisValue}<br/>Lessons: ${p.data}`;
      },
    },
    grid: { top: 40, left: 40, right: 16, bottom: 80 },
    xAxis: {
      type: "category",
      data: labels,
      axisLabel: {
        interval: 0,
        rotate: labels.length > 4 ? 30 : 0,
        fontSize: 11,
      },
    },
    yAxis: {
      type: "value",
      name: "Lessons",
      minInterval: 1,
    },
    series: [
      {
        name: "Lessons",
        type: "bar",
        data: lessons,
        barWidth: "60%",
        itemStyle: { borderRadius: [6, 6, 0, 0] },
      },
    ],
  };
});

/* ------------------------------------------------
 * Table data
 * ------------------------------------------------ */

// small helper type so TS is happy even if backend later adds class_name / total_records
type TopAbsentStudentRow = {
  student_id: string;
  student_name: string;
  absent_count: number;
  class_name?: string | null;
  class_id?: string | null;
  total_records?: number | null;
};

/**
 * We normalise the data here so UI does not show blank cells
 * even if backend does not send class_name / total_records yet.
 */
const topAbsentStudents = computed<TopAbsentStudentRow[]>(() => {
  const raw: any[] = attendance.value?.top_absent_students ?? [];
  console.log(raw);
  return raw.map((row) => ({
    ...row,
    // class_name is not in the sample payload, so give a readable fallback
    class_name:
      row.class_name ??
      row.class_label ?? // in case backend adds a different key later
      "Unknown",
    // total_records: fallback to absent_count if backend does not send total_records
    total_records:
      row.total_records != null ? row.total_records : row.absent_count ?? 0,
  }));
});

const passRateRows = computed(() => grades.value?.pass_rate_by_class ?? []);

const scheduleTeacherRows = computed(
  () => schedule.value?.lessons_by_teacher ?? []
);
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Header -->
    <OverviewHeader
      title="Admin Dashboard"
      description="High-level overview of attendance, grades, and schedule across the school."
      :loading="loading"
      :showRefresh="false"
    >
      <template #icon>
        <span
          class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-[var(--color-primary-light-6)] text-[color:var(--color-primary)] border border-[color:var(--color-primary-light-4)]"
        >
          {{ activeFilterLabel }}
        </span>
      </template>

      <template #actions>
        <div class="flex flex-wrap items-center gap-2">
          <el-date-picker
            v-model="filterDateRange"
            type="daterange"
            size="small"
            range-separator="→"
            start-placeholder="From"
            end-placeholder="To"
            format="YYYY-MM-DD"
          />
          <el-select
            v-model="filterTerm"
            placeholder="Term"
            size="small"
            style="min-width: 140px"
          >
            <el-option
              v-for="t in termOptions"
              :key="t.value || 'all'"
              :label="t.label"
              :value="t.value"
            />
          </el-select>

          <BaseButton
            plain
            :loading="loading"
            class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
            @click="loadDashboard"
          >
            Apply filters
          </BaseButton>
        </div>
      </template>
    </OverviewHeader>

    <!-- Error -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mb-2"
    />

    <!-- Overview cards -->
    <el-row :gutter="16">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Total students</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalStudents }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Total teachers</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalTeachers }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Total classes</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalClasses }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Total subjects</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalSubjects }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 1: Attendance overview -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Attendance status summary</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="attendanceStatusOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="16">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Daily attendance trend</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="attendanceDailyTrendOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 2: Attendance by class + top absent students -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Attendance by class</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="attendanceByClassOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Top absent students</div>

          <el-table
            :data="topAbsentStudents"
            size="small"
            style="width: 100%"
            :height="260"
            border
          >
            <el-table-column
              prop="student_name"
              label="Student"
              min-width="160"
              show-overflow-tooltip
            />
            <el-table-column
              prop="class_name"
              label="Class"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column prop="absent_count" label="Absent" width="80" />
            <el-table-column
              prop="total_records"
              label="Total records"
              width="110"
            />
            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No data available.
              </div>
            </template>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 3: Grade overview -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Average score by subject</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="gradeAvgBySubjectOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Score distribution</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="gradeDistributionOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 4: Pass rate by class -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Pass rate by class</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="passRateByClassOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Pass-rate details</div>
          <el-table
            :data="passRateRows"
            size="small"
            style="width: 100%"
            :height="260"
            border
          >
            <el-table-column
              prop="class_name"
              label="Class"
              min-width="150"
              show-overflow-tooltip
            />
            <el-table-column prop="avg_score" label="Avg score" width="100">
              <template #default="{ row }">
                {{ row.avg_score.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="pass_rate" label="Pass rate" width="100">
              <template #default="{ row }">
                {{ (row.pass_rate * 100).toFixed(1) }}%
              </template>
            </el-table-column>
            <el-table-column prop="passed" label="Passed" width="80" />
            <el-table-column prop="total_students" label="Total" width="80" />
            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No data available.
              </div>
            </template>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 5: Schedule overview -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Lessons by weekday</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="scheduleByWeekdayOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loading" class="mb-4">
          <div class="font-semibold mb-2">Teaching load by teacher</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="scheduleByTeacherOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[260px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>

          <el-table
            :data="scheduleTeacherRows"
            size="small"
            style="width: 100%"
            :height="200"
            border
            class="mt-3"
          >
            <el-table-column
              prop="teacher_name"
              label="Teacher"
              min-width="160"
              show-overflow-tooltip
            />
            <el-table-column prop="lessons" label="Lessons" width="90" />
            <el-table-column prop="classes" label="Classes" width="90" />
            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No data available.
              </div>
            </template>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped></style>
