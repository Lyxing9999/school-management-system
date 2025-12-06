<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";

import { teacherService } from "~/api/teacher";
import { formatDate } from "~/utils/formatDate";

import type {
  ClassSectionDTO,
  GradeDTO,
  AttendanceDTO,
} from "~/api/types/school.dto";
import type { TeacherScheduleDTO } from "~/api/teacher/dto";

definePageMeta({
  layout: "teacher",
});

const teacher = teacherService();

/* ------------------------------------------------
 * Types
 * ------------------------------------------------ */

type TeacherClassEnriched = ClassSectionDTO & {
  student_count?: number;
  subject_count?: number;
  teacher_name?: string;
  subject_labels?: string[];
};

type TeacherGradeEnriched = GradeDTO & {
  class_name?: string;
  subject_label?: string;
  student_name?: string;
};

type TeacherAttendanceEnriched = AttendanceDTO & {
  class_name?: string;
  student_name?: string;
  teacher_name?: string;
};

type TeacherScheduleItem = TeacherScheduleDTO & {
  class_name?: string;
  subject_label?: string;
  teacher_name?: string;
  room?: string;
  day_of_week: number; // 1=Mon..7=Sun
  start_time: string;
  end_time: string;
};

/* ------------------------------------------------
 * State
 * ------------------------------------------------ */

const loadingOverview = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<TeacherClassEnriched[]>([]);
const grades = ref<TeacherGradeEnriched[]>([]);
const schedule = ref<TeacherScheduleItem[]>([]);
const attendance = ref<TeacherAttendanceEnriched[]>([]);

const defaultClassId = ref<string | null>(null);

/* ------------------------------------------------
 * Helpers
 * ------------------------------------------------ */

const weekdayShortLabels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

const extractErrorMessage = (err: unknown, fallback: string): string => {
  if (err instanceof Error && err.message) return err.message;
  if (typeof err === "string") return err;
  return fallback;
};

/**
 * Normalize API responses that may be either:
 * - { items: T[] }
 * - T[]
 * - null / undefined
 */
function normalizeItems<T>(res: { items?: T[] } | T[] | null | undefined): T[] {
  if (!res) return [];
  if (Array.isArray(res)) return res;
  return res.items ?? [];
}

/* ------------------------------------------------
 * Load overview data
 * ------------------------------------------------ */

const loadOverview = async () => {
  loadingOverview.value = true;
  errorMessage.value = null;

  try {
    const [classesRes, scheduleRes] = await Promise.all([
      teacher.teacher.listMyClasses({ showError: false }),
      teacher.teacher.listMySchedule({ showError: false }),
    ]);

    classes.value = normalizeItems<TeacherClassEnriched>(
      classesRes as { items?: TeacherClassEnriched[] } | TeacherClassEnriched[]
    );

    schedule.value = normalizeItems<TeacherScheduleItem>(
      scheduleRes as { items?: TeacherScheduleItem[] } | TeacherScheduleItem[]
    );

    if (!defaultClassId.value && classes.value.length > 0) {
      defaultClassId.value = classes.value[0].id;
    }

    if (defaultClassId.value) {
      const [gradesRes, attendanceRes] = await Promise.all([
        teacher.teacher.listGradesForClass(defaultClassId.value, {
          showError: false,
        }),
        teacher.teacher.listAttendanceForClass(defaultClassId.value, {
          showError: false,
        }),
      ]);

      grades.value = normalizeItems<TeacherGradeEnriched>(
        gradesRes as { items?: TeacherGradeEnriched[] } | TeacherGradeEnriched[]
      );

      attendance.value = normalizeItems<TeacherAttendanceEnriched>(
        attendanceRes as
          | { items?: TeacherAttendanceEnriched[] }
          | TeacherAttendanceEnriched[]
      );
    } else {
      grades.value = [];
      attendance.value = [];
    }
  } catch (err: unknown) {
    console.error(err);
    const message = extractErrorMessage(
      err,
      "Failed to load teacher dashboard data."
    );
    errorMessage.value = message;
    ElMessage.error(message);
  } finally {
    loadingOverview.value = false;
  }
};

/* ------------------------------------------------
 * Stats
 * ------------------------------------------------ */

const totalClasses = computed(() => classes.value.length);

const totalStudents = computed(() =>
  classes.value.reduce((sum, c) => {
    if (typeof c.student_count === "number") return sum + c.student_count;
    if (Array.isArray((c as any).student_ids)) {
      return sum + (c as any).student_ids.length;
    }
    return sum;
  }, 0)
);

const totalSubjects = computed(() =>
  classes.value.reduce((sum, c) => {
    if (typeof c.subject_count === "number") return sum + c.subject_count;
    if (Array.isArray((c as any).subject_ids)) {
      return sum + (c as any).subject_ids.length;
    }
    return sum;
  }, 0)
);

// backend uses 1=Mon..7=Sun
const todayDayOfWeek = computed(() => {
  const jsDay = new Date().getDay(); // 0=Sun..6=Sat
  return jsDay === 0 ? 7 : jsDay;
});

const todaySchedule = computed(() =>
  schedule.value.filter((s) => s.day_of_week === todayDayOfWeek.value)
);

const recentAttendance = computed(() =>
  attendance.value
    .slice()
    .sort(
      (a, b) =>
        new Date(b.record_date).getTime() - new Date(a.record_date).getTime()
    )
    .slice(0, 8)
);

const defaultClassName = computed(() => {
  if (!defaultClassId.value) return null;
  return classes.value.find((c) => c.id === defaultClassId.value)?.name ?? null;
});

/* ------------------------------------------------
 * Lifecycle
 * ------------------------------------------------ */

onMounted(async () => {
  await loadOverview();
});

/* ------------------------------------------------
 * Demo data for charts (when backend is empty)
 * ------------------------------------------------ */

const demoAttendanceBuckets = [
  { status: "present", count: 40 },
  { status: "absent", count: 6 },
  { status: "excused", count: 4 },
];

const demoGradeItemsByType = [
  { type: "quiz", score: 78 },
  { type: "quiz", score: 85 },
  { type: "exam", score: 62 },
  { type: "exam", score: 58 },
  { type: "assignment", score: 90 },
  { type: "assignment", score: 82 },
];

/* ------------------------------------------------
 * Chart options
 * ------------------------------------------------ */

/** 1) Teaching load by weekday (lessons per day) */
const scheduleByDayOption = computed(() => {
  const counts: number[] = [];
  for (let day = 1; day <= 7; day++) {
    const lessonsForDay = schedule.value.filter((s) => s.day_of_week === day);
    counts.push(lessonsForDay.length);
  }
  return {
    tooltip: { trigger: "axis" },
    grid: { top: 24, left: 40, right: 16, bottom: 40 },
    xAxis: {
      type: "category",
      data: weekdayShortLabels,
      axisTick: { alignWithLabel: true },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      name: "Lessons",
    },
    series: [
      {
        name: "Lessons",
        data: counts,
        type: "bar",
        barWidth: "50%",
        itemStyle: { borderRadius: [6, 6, 0, 0] },
      },
    ],
  };
});

/** 2) Grade overview by subject (avg score) */
const gradeBySubjectOption = computed(() => {
  if (!grades.value.length) {
    // Fallback demo data so the chart still shows structure
    const demoLabels = ["Math", "Khmer", "English", "Physics"];
    const demoValues = [82, 75, 88, 70];
    return {
      tooltip: { trigger: "axis" },
      grid: { top: 24, left: 40, right: 16, bottom: 80 },
      xAxis: {
        type: "category",
        data: demoLabels,
        axisLabel: {
          interval: 0,
          rotate: demoLabels.length > 4 ? 30 : 0,
          fontSize: 11,
        },
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 100,
        name: "Avg score",
      },
      series: [
        {
          name: "Average score",
          type: "bar",
          data: demoValues,
          barWidth: "60%",
          itemStyle: { borderRadius: [6, 6, 0, 0] },
        },
      ],
    };
  }

  const map = new Map<string, { total: number; count: number }>();

  for (const g of grades.value) {
    const key = g.subject_label || "Unknown subject";
    const prev = map.get(key) ?? { total: 0, count: 0 };
    prev.total += g.score;
    prev.count += 1;
    map.set(key, prev);
  }

  const labels = Array.from(map.keys());
  const averages = labels.map((label) => {
    const agg = map.get(label)!;
    return Number((agg.total / agg.count).toFixed(2));
  });

  return {
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.axisValue}<br/>Avg score: ${p.data}`;
      },
    },
    grid: { top: 24, left: 40, right: 16, bottom: 80 },
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
      min: 0,
      max: 100,
      name: "Avg score",
    },
    series: [
      {
        name: "Average score",
        type: "bar",
        data: averages,
        barWidth: "60%",
        itemStyle: { borderRadius: [6, 6, 0, 0] },
      },
    ],
  };
});

/** 3) Attendance overview (present / absent / excused) */
const attendanceStatusOption = computed(() => {
  // Use real attendance if available, else demo buckets
  if (attendance.value.length === 0) {
    const data = demoAttendanceBuckets.map((b) => ({
      name: b.status,
      value: b.count,
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
          itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 1 },
          data,
        },
      ],
    };
  }

  const counts: Record<string, number> = {};
  for (const a of attendance.value) {
    const s = a.status || "unknown";
    counts[s] = (counts[s] || 0) + 1;
  }

  const data = Object.entries(counts).map(([name, value]) => ({ name, value }));

  return {
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [
      {
        name: "Attendance",
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 6, borderColor: "#fff", borderWidth: 1 },
        data,
      },
    ],
  };
});

/** 4) Performance by assessment type (quiz / exam / assignment) */
const gradeByTypeOption = computed(() => {
  // If no real grades yet, use demo items
  const source =
    grades.value.length === 0
      ? demoGradeItemsByType
      : grades.value.map((g) => ({ type: g.type, score: g.score }));

  if (!source.length) {
    return {
      title: { text: "No grade data yet", left: "center", top: "center" },
    };
  }

  const map = new Map<string, { total: number; count: number }>();

  for (const g of source) {
    const key = g.type || "unknown";
    const prev = map.get(key) ?? { total: 0, count: 0 };
    prev.total += g.score;
    prev.count += 1;
    map.set(key, prev);
  }

  const labels = Array.from(map.keys());
  const averages = labels.map((label) => {
    const agg = map.get(label)!;
    return Number((agg.total / agg.count).toFixed(2));
  });

  return {
    tooltip: { trigger: "axis" },
    grid: { top: 24, left: 40, right: 16, bottom: 40 },
    xAxis: { type: "category", data: labels },
    yAxis: {
      type: "value",
      min: 0,
      max: 100,
      name: "Avg score",
    },
    series: [
      {
        name: "Average score",
        type: "bar",
        data: averages,
        barWidth: "50%",
        itemStyle: { borderRadius: [6, 6, 0, 0] },
      },
    ],
  };
});
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Header -->
    <div
      class="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-[var(--color-primary-light-9)] to-[var(--color-primary-light-9)] border border-[color:var(--color-primary-light-9)] shadow-sm rounded-2xl p-5"
    >
      <div>
        <h1
          class="text-2xl font-bold flex items-center gap-2 text-[color:var(--color-dark)]"
        >
          Teacher Dashboard
          <span
            v-if="defaultClassName"
            class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-[var(--color-primary-light-6)] text-[color:var(--color-primary)] border border-[color:var(--color-primary-light-4)]"
          >
            Focus: {{ defaultClassName }}
          </span>
        </h1>

        <p class="mt-1.5 text-sm text-[color:var(--color-primary-light-1)]">
          Overview of your classes, teaching load, student performance, and
          attendance for your focus class.
        </p>

        <p v-if="!defaultClassName" class="text-[11px] text-gray-500 mt-1">
          Assign a class to see focus grades and attendance here.
        </p>
      </div>

      <div class="flex items-center gap-2 justify-end">
        <BaseButton
          plain
          :loading="loadingOverview"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="loadOverview"
        >
          Refresh
        </BaseButton>
      </div>
    </div>

    <!-- Error -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mb-2"
    />

    <!-- Stats Row -->
    <el-row :gutter="16">
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Classes you teach</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalClasses }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Total students</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalStudents }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Subjects taught</div>
          <div class="text-2xl font-semibold mt-1">
            {{ totalSubjects }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Today&apos;s Lessons</div>
          <div class="text-2xl font-semibold mt-1">
            {{ todaySchedule.length }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 1: Schedule + Grade by subject -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loadingOverview" class="mb-4">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Teaching Schedule Overview</div>
              <div class="text-xs text-gray-500">
                Number of lessons you teach on each day of the week.
              </div>
            </div>
          </div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="scheduleByDayOption"
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
        <el-card shadow="hover" v-loading="loadingOverview" class="mb-4">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Grade Overview (focus class)</div>
              <div class="text-xs text-gray-500">
                Average score per subject in your focus class.
              </div>
            </div>
          </div>

          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="gradeBySubjectOption"
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

          <p class="mt-2 text-[11px] text-gray-500">
            Tip: Quickly see which subjects are strong and which may need more
            attention.
          </p>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 2: Attendance + Grade by type -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loadingOverview" class="mb-4">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Attendance Overview</div>
              <div class="text-xs text-gray-500">
                Distribution of present, absent, and excused records in the
                focus class.
              </div>
            </div>
          </div>

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

          <p class="mt-2 text-[11px] text-gray-500">
            Tip: If absences are high, use the table below to see which students
            need follow-up.
          </p>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loadingOverview" class="mb-4">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Performance by Assessment Type</div>
              <div class="text-xs text-gray-500">
                Average scores for quizzes, exams, and assignments.
              </div>
            </div>
          </div>

          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="gradeByTypeOption"
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

          <p class="mt-2 text-[11px] text-gray-500">
            Tip: If exams are much lower than quizzes, it may indicate test
            difficulty or preparation issues.
          </p>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Attendance row -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24">
        <el-card shadow="hover">
          <div class="flex justify-between items-center mb-2">
            <div>
              <div class="font-semibold">Recent Attendance (focus class)</div>
              <div class="text-xs text-gray-500">
                Latest attendance records you marked for the focus class.
              </div>
            </div>
          </div>

          <el-table
            :data="recentAttendance"
            v-loading="loadingOverview"
            size="small"
            style="width: 100%"
            :height="320"
            border
          >
            <el-table-column prop="record_date" label="Date" min-width="130">
              <template #default="{ row }">
                {{ formatDate(row.record_date) }}
              </template>
            </el-table-column>

            <el-table-column
              prop="student_name"
              label="Student"
              min-width="160"
              show-overflow-tooltip
            />

            <el-table-column prop="status" label="Status" min-width="120">
              <template #default="{ row }">
                <el-tag
                  size="small"
                  :type="
                    row.status === 'present'
                      ? 'success'
                      : row.status === 'excused'
                      ? 'warning'
                      : 'danger'
                  "
                >
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column
              prop="class_name"
              label="Class"
              min-width="160"
              show-overflow-tooltip
            />

            <el-table-column
              prop="created_at"
              label="Recorded At"
              min-width="180"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>

            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No attendance records yet for the focus class.
              </div>
            </template>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
/* Keep this file clean; add styles only when really needed */
</style>
