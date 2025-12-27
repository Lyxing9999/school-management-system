<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";

import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import { formatDate } from "~/utils/formatDate";
import { reportError, invariant } from "~/utils/errors";
definePageMeta({
  layout: "student",
});

/**
 * Demo mode:
 * - true  => uses local demo arrays (your Mongo sample-based)
 * - false => use your real studentService() calls
 */
const USE_DEMO = true;

/* ------------------------------------------------
 * Types (frontend view models)
 * ------------------------------------------------ */

type StudentClassDTO = {
  id: string;
  name: string;
  teacher_id?: string | null;
  subject_ids?: string[];
};

type SubjectDTO = {
  id: string;
  name: string;
  code: string;
};

type GradeDTO = {
  id: string;
  student_id: string;
  subject_id: string;
  class_id?: string | null;
  teacher_id?: string | null;
  term?: string | null;
  type: string;
  score: number;
  created_at: string;

  // display
  subject_label?: string;
  class_name?: string;
};

type AttendanceDTO = {
  id: string;
  student_id: string;
  class_id: string;
  status: "present" | "absent" | "late" | "excused" | string;
  record_date: string;
  marked_by_teacher_id?: string | null;
  created_at: string;

  // display
  class_name?: string;
  teacher_name?: string;
};

type ScheduleDTO = {
  id: string;
  class_id: string;
  teacher_id: string;
  day_of_week: number; // 1=Mon..7=Sun
  start_time: string; // "HH:MM"
  end_time: string; // "HH:MM"
  room?: string | null;

  // display
  class_name?: string;
  teacher_name?: string;
  subject_id?: string | null;
};

type StudentDashboardFilterDTO = {
  date_from?: string;
  date_to?: string;
  term?: string;
  class_id?: string;
};

/* ------------------------------------------------
 * State (admin-like)
 * ------------------------------------------------ */

const loading = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<StudentClassDTO[]>([]);
const subjects = ref<SubjectDTO[]>([]);
const grades = ref<GradeDTO[]>([]);
const schedule = ref<ScheduleDTO[]>([]);
const attendance = ref<AttendanceDTO[]>([]);

/** Filters (same UX as admin) */
const filterDateRange = ref<[Date, Date] | null>(null);
const filterTerm = ref<string | "">("");
const filterClassId = ref<string | "">("");

const termOptions = [
  { label: "All terms", value: "" },
  { label: "Semester 1", value: "S1" },
  { label: "Semester 2", value: "S2" },
];

/* ------------------------------------------------
 * Helpers (admin pattern)
 * ------------------------------------------------ */

const extractErrorMessage = (err: unknown, fallback: string): string => {
  if (err instanceof Error && err.message) return err.message;
  if (typeof err === "string") return err;
  // common backend shape
  // @ts-ignore
  if (err?.message) return String((err as any).message);
  return fallback;
};

const formatDateParam = (d: Date): string => d.toISOString().slice(0, 10);

const buildFilterPayload = (): StudentDashboardFilterDTO => {
  const filters: StudentDashboardFilterDTO = {};

  if (filterDateRange.value) {
    const [start, end] = filterDateRange.value;
    filters.date_from = formatDateParam(start);
    filters.date_to = formatDateParam(end);
  }

  if (filterTerm.value) filters.term = filterTerm.value;
  if (filterClassId.value) filters.class_id = filterClassId.value;

  return filters;
};

const withinDateRange = (iso: string) => {
  if (!filterDateRange.value) return true;
  const [start, end] = filterDateRange.value;
  const t = new Date(iso).getTime();
  const s = new Date(start).setHours(0, 0, 0, 0);
  const e = new Date(end).setHours(23, 59, 59, 999);
  return t >= s && t <= e;
};

/* ------------------------------------------------
 * Demo data (built from your Mongo samples)
 * ------------------------------------------------ */

const loadDemoData = () => {
  // Subjects (your sample)
  const subj: SubjectDTO[] = [
    { id: "69253bac9e97249bcea9ae27", name: "Match", code: "M-002" },
    { id: "6928ed432292879b7a3a6b95", name: "Science", code: "S-001" },
    { id: "693b96301213164a63ad5539", name: "Math", code: "M-001" },
  ];

  // Classes (your sample)
  const cls: StudentClassDTO[] = [
    {
      id: "693d5f09488a6ba4642705d3",
      name: "Grade 9",
      teacher_id: "693d5eaf6a58b8b90b4078f5",
      subject_ids: ["693b96301213164a63ad5539"],
    },
    {
      id: "6928ed5f2292879b7a3a6b96",
      name: "Grade 10",
      teacher_id: "69252fd678b90ceeb4b58081",
      subject_ids: ["6928ed432292879b7a3a6b95"],
    },
  ];

  // Schedule (your sample + a couple more)
  const sch: ScheduleDTO[] = [
    {
      id: "692f17d8408e11eb0e23aa87",
      class_id: "692e77744863b4739c8017d1",
      teacher_id: "692cf0759c755837d27af7a7",
      day_of_week: 1,
      start_time: "08:00",
      end_time: "09:00",
      room: "asdf",
      class_name: "Grade 9",
      teacher_name: "Mr. Teacher",
      subject_id: "693b96301213164a63ad5539",
    },
    {
      id: "sch-2",
      class_id: "693d5f09488a6ba4642705d3",
      teacher_id: "693d5eaf6a58b8b90b4078f5",
      day_of_week: 3,
      start_time: "10:00",
      end_time: "11:00",
      room: "A101",
      class_name: "Grade 9",
      teacher_name: "Mr. Dara",
      subject_id: "693b96301213164a63ad5539",
    },
  ];

  // Grades (your sample + more points for charts)
  const grd: GradeDTO[] = [
    {
      id: "692998034cdff1a47715b93a",
      student_id: "69252fa678b90ceeb4b58080",
      subject_id: "6928ed432292879b7a3a6b95",
      class_id: "6928ed5f2292879b7a3a6b96",
      teacher_id: "69252fd678b90ceeb4b58081",
      term: "S1",
      type: "exam",
      score: 13,
      created_at: "2025-11-28T12:39:31.753Z",
    },
    {
      id: "g-2",
      student_id: "69252fa678b90ceeb4b58080",
      subject_id: "693b96301213164a63ad5539",
      class_id: "693d5f09488a6ba4642705d3",
      teacher_id: "693d5eaf6a58b8b90b4078f5",
      term: "S1",
      type: "quiz",
      score: 68,
      created_at: "2025-12-01T08:10:00.000Z",
    },
    {
      id: "g-3",
      student_id: "69252fa678b90ceeb4b58080",
      subject_id: "693b96301213164a63ad5539",
      class_id: "693d5f09488a6ba4642705d3",
      teacher_id: "693d5eaf6a58b8b90b4078f5",
      term: "S1",
      type: "homework",
      score: 74,
      created_at: "2025-12-05T09:30:00.000Z",
    },
    {
      id: "g-4",
      student_id: "69252fa678b90ceeb4b58080",
      subject_id: "6928ed432292879b7a3a6b95",
      class_id: "6928ed5f2292879b7a3a6b96",
      teacher_id: "69252fd678b90ceeb4b58081",
      term: "S2",
      type: "quiz",
      score: 55,
      created_at: "2025-12-10T09:30:00.000Z",
    },
  ];

  // Attendance (your sample + more points)
  const att: AttendanceDTO[] = [
    {
      id: "6927dd579702ccf745db7d2b",
      student_id: "6925687810b67780c6f740b1",
      class_id: "69253bc39e97249bcea9ae28",
      status: "absent",
      record_date: "2025-11-27T00:00:00.000Z",
      marked_by_teacher_id: "69252fd678b90ceeb4b58081",
      created_at: "2025-11-27T05:10:47.973Z",
    },
    {
      id: "a-2",
      student_id: "6925687810b67780c6f740b1",
      class_id: "693d5f09488a6ba4642705d3",
      status: "present",
      record_date: "2025-12-01T00:00:00.000Z",
      marked_by_teacher_id: "693d5eaf6a58b8b90b4078f5",
      created_at: "2025-12-01T05:10:47.973Z",
    },
    {
      id: "a-3",
      student_id: "6925687810b67780c6f740b1",
      class_id: "693d5f09488a6ba4642705d3",
      status: "late",
      record_date: "2025-12-05T00:00:00.000Z",
      marked_by_teacher_id: "693d5eaf6a58b8b90b4078f5",
      created_at: "2025-12-05T05:10:47.973Z",
    },
    {
      id: "a-4",
      student_id: "6925687810b67780c6f740b1",
      class_id: "693d5f09488a6ba4642705d3",
      status: "excused",
      record_date: "2025-12-10T00:00:00.000Z",
      marked_by_teacher_id: "693d5eaf6a58b8b90b4078f5",
      created_at: "2025-12-10T05:10:47.973Z",
    },
  ];

  // Attach display labels (join)
  const classMap = new Map(cls.map((c) => [c.id, c.name]));
  const subjectMap = new Map(subj.map((s) => [s.id, s.name]));

  const withGradeLabels = grd.map((g) => ({
    ...g,
    class_name: g.class_id ? classMap.get(g.class_id) : undefined,
    subject_label: subjectMap.get(g.subject_id) || g.subject_id,
  }));

  const withAttendanceLabels = att.map((a) => ({
    ...a,
    class_name: classMap.get(a.class_id) || a.class_id,
    teacher_name: "Teacher", // demo placeholder
  }));

  subjects.value = subj;
  classes.value = cls;
  grades.value = withGradeLabels;
  schedule.value = sch;
  attendance.value = withAttendanceLabels;

  // default class filter
  if (!filterClassId.value && classes.value.length) {
    filterClassId.value = classes.value[0].id;
  }
};

/* ------------------------------------------------
 * Load dashboard (demo or real)
 * ------------------------------------------------ */

const loadDashboard = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const filters = buildFilterPayload();

    if (USE_DEMO) {
      loadDemoData();
      // apply "selected class" to attendance in UI via computed filtering below
      return;
    }

    // If you want the real API later, plug your studentService calls here
    // const studentApi = studentService();
    // ...
    // classes.value = ...
    // schedule.value = ...
    // grades.value = ...
    // attendance.value = ...

    invariant(
      false,
      "Student dashboard API is not wired while USE_DEMO=false."
    );
  } catch (err) {
    reportError(err, "student.dashboard.load", "log");
    const message = extractErrorMessage(
      err,
      "Failed to load student dashboard data."
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
 * Computed filtering
 * ------------------------------------------------ */

const filteredGrades = computed(() => {
  let rows = grades.value.slice();

  if (filterTerm.value)
    rows = rows.filter((g) => (g.term ?? "") === filterTerm.value);
  if (filterDateRange.value)
    rows = rows.filter((g) => withinDateRange(g.created_at));

  return rows;
});

const filteredAttendance = computed(() => {
  let rows = attendance.value.slice();

  if (filterClassId.value)
    rows = rows.filter((a) => a.class_id === filterClassId.value);
  if (filterDateRange.value)
    rows = rows.filter((a) => withinDateRange(a.record_date));

  return rows;
});

/* ------------------------------------------------
 * Summary stats
 * ------------------------------------------------ */

const totalClasses = computed(() => classes.value.length);

const totalSubjects = computed(() => {
  const set = new Set<string>();
  for (const c of classes.value)
    (c.subject_ids ?? []).forEach((sid) => set.add(sid));
  return set.size;
});

const averageScore = computed(() => {
  if (!filteredGrades.value.length) return null;
  const total = filteredGrades.value.reduce(
    (sum, g) => sum + (g.score ?? 0),
    0
  );
  return total / filteredGrades.value.length;
});

// today schedule (1..7)
const todayDayOfWeek = computed(() => {
  const jsDay = new Date().getDay(); // 0=Sun..6=Sat
  return jsDay === 0 ? 7 : jsDay;
});
const todaySchedule = computed(() =>
  schedule.value.filter((s) => s.day_of_week === todayDayOfWeek.value)
);

const recentGrades = computed(() =>
  filteredGrades.value
    .slice()
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    .slice(0, 5)
);

const recentAttendance = computed(() =>
  filteredAttendance.value
    .slice()
    .sort(
      (a, b) =>
        new Date(b.record_date).getTime() - new Date(a.record_date).getTime()
    )
    .slice(0, 8)
);

/* ------------------------------------------------
 * Visualizations (ECharts options, same pattern as admin)
 * ------------------------------------------------ */

// Attendance summary donut
const attendanceStatusOption = computed(() => {
  const rows = filteredAttendance.value;
  if (!rows.length) {
    return {
      title: { text: "No attendance data", left: "center", top: "center" },
    };
  }

  const counts = new Map<string, number>();
  for (const r of rows) counts.set(r.status, (counts.get(r.status) ?? 0) + 1);

  const seriesData = Array.from(counts.entries()).map(([name, value]) => ({
    name,
    value,
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
        data: seriesData,
      },
    ],
  };
});

// Score trend line (by grade created_at)
const scoreTrendOption = computed(() => {
  const rows = filteredGrades.value
    .slice()
    .sort(
      (a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );

  if (!rows.length) {
    return { title: { text: "No grade data", left: "center", top: "center" } };
  }

  const x = rows.map((r) => formatDate(r.created_at));
  const y = rows.map((r) => r.score);

  return {
    tooltip: { trigger: "axis" },
    grid: { top: 40, left: 40, right: 16, bottom: 40 },
    xAxis: { type: "category", data: x },
    yAxis: { type: "value", name: "Score", min: 0, max: 100 },
    series: [{ name: "Score", type: "line", smooth: true, data: y }],
  };
});

// Avg score by subject (bar)
const avgBySubjectOption = computed(() => {
  const rows = filteredGrades.value;
  if (!rows.length) {
    return { title: { text: "No grade data", left: "center", top: "center" } };
  }

  const map = new Map<
    string,
    { label: string; total: number; count: number; avg: number }
  >();
  for (const g of rows) {
    const label = g.subject_label || g.subject_id;
    const cur = map.get(label) || { label, total: 0, count: 0, avg: 0 };
    cur.total += g.score ?? 0;
    cur.count += 1;
    cur.avg = cur.total / cur.count;
    map.set(label, cur);
  }

  const seriesRows = Array.from(map.values()).sort((a, b) => b.avg - a.avg);
  const labels = seriesRows.map((r) => r.label);
  const values = seriesRows.map((r) => Number(r.avg.toFixed(1)));

  return {
    tooltip: { trigger: "axis" },
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
    yAxis: { type: "value", name: "Avg score", min: 0, max: 100 },
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

/* ------------------------------------------------
 * COO-style score insights (right card)
 * ------------------------------------------------ */

const lastNGrades = computed(() =>
  filteredGrades.value
    .slice()
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
    .slice(0, 10)
);

const lastNAvg = computed(() => {
  if (!lastNGrades.value.length) return null;
  const total = lastNGrades.value.reduce((sum, g) => sum + (g.score ?? 0), 0);
  return total / lastNGrades.value.length;
});

const scoreTrendMeta = computed(() => {
  if (averageScore.value === null || lastNAvg.value === null) return null;
  const diff = lastNAvg.value - averageScore.value;
  return { diff, direction: diff > 1 ? "up" : diff < -1 ? "down" : "flat" };
});

const riskFlag = computed(() => {
  if (averageScore.value === null) return null;
  if (averageScore.value < 50)
    return { level: "high" as const, label: "High risk" };
  if (averageScore.value < 65)
    return { level: "medium" as const, label: "Medium risk" };
  return { level: "low" as const, label: "Low risk" };
});

/* ------------------------------------------------
 * Active filter label (admin pattern)
 * ------------------------------------------------ */

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

  if (filterClassId.value) {
    const classLabel =
      classes.value.find((c) => c.id === filterClassId.value)?.name || "Class";
    parts.push(`Class: ${classLabel}`);
  }

  if (!parts.length) return "Showing all available data";
  return parts.join(" • ");
});
</script>

<template>
  <div class="p-4 space-y-4">
    <OverviewHeader
      title="Student Dashboard"
      description="Your performance and attendance overview."
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

          <el-select
            v-model="filterClassId"
            placeholder="Class"
            size="small"
            style="min-width: 170px"
            clearable
          >
            <el-option
              v-for="c in classes"
              :key="c.id"
              :label="c.name"
              :value="c.id"
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
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Enrolled Classes</div>
          <div class="text-2xl font-semibold">{{ totalClasses }}</div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Total Subjects</div>
          <div class="text-2xl font-semibold">{{ totalSubjects }}</div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Average Score</div>
          <div class="text-2xl font-semibold">
            <span v-if="averageScore !== null">{{
              averageScore.toFixed(1)
            }}</span>
            <span v-else class="text-gray-400">N/A</span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500 mb-1">Attendance Records</div>
          <div class="text-2xl font-semibold">
            {{ filteredAttendance.length }}
          </div>
          <div class="text-[10px] text-gray-400 mt-1">For selected filters</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row: Left (tables) | Right (insights + charts) -->
    <el-row :gutter="16">
      <!-- LEFT -->
      <el-col :xs="24" :md="14">
        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-2">Today&apos;s Schedule</div>
          <el-table
            :data="todaySchedule"
            size="small"
            border
            style="width: 100%"
          >
            <el-table-column
              prop="class_name"
              label="Class"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column
              prop="teacher_name"
              label="Teacher"
              min-width="120"
              show-overflow-tooltip
            />
            <el-table-column label="Time" min-width="110">
              <template #default="{ row }"
                >{{ row.start_time }} - {{ row.end_time }}</template
              >
            </el-table-column>
            <el-table-column
              prop="room"
              label="Room"
              min-width="90"
              show-overflow-tooltip
            />
            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No lessons scheduled for today.
              </div>
            </template>
          </el-table>
        </el-card>

        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-2">Recent Grades</div>
          <el-table
            :data="recentGrades"
            size="small"
            border
            style="width: 100%"
          >
            <el-table-column
              prop="subject_label"
              label="Subject"
              min-width="160"
              show-overflow-tooltip
            />
            <el-table-column
              prop="class_name"
              label="Class"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column prop="score" label="Score" width="90" />
            <el-table-column prop="type" label="Type" width="100" />
            <el-table-column prop="term" label="Term" width="80" />
            <el-table-column
              prop="created_at"
              label="Recorded At"
              min-width="170"
              show-overflow-tooltip
            >
              <template #default="{ row }">{{
                formatDate(row.created_at)
              }}</template>
            </el-table-column>
            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No grade data for current filters.
              </div>
            </template>
          </el-table>
        </el-card>

        <el-card shadow="hover" v-loading="loading">
          <div class="font-semibold mb-2">Recent Attendance</div>
          <el-table
            :data="recentAttendance"
            size="small"
            border
            style="width: 100%"
          >
            <el-table-column prop="record_date" label="Date" min-width="130">
              <template #default="{ row }">{{
                formatDate(row.record_date)
              }}</template>
            </el-table-column>
            <el-table-column
              prop="class_name"
              label="Class"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column prop="status" label="Status" width="110">
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
              prop="created_at"
              label="Recorded At"
              min-width="170"
            >
              <template #default="{ row }">{{
                formatDate(row.created_at)
              }}</template>
            </el-table-column>

            <template #empty>
              <div class="text-center text-gray-500 text-xs py-3">
                No attendance data for current filters.
              </div>
            </template>
          </el-table>
        </el-card>
      </el-col>

      <!-- RIGHT -->
      <el-col :xs="24" :md="10">
        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-1">Score Insights</div>
          <div class="text-xs text-gray-500 mb-3">
            Overall score, recent trend, and risk indicator.
          </div>

          <div class="grid grid-cols-2 gap-3 mb-3">
            <div class="p-3 rounded border">
              <div class="text-xs text-gray-500">Overall Avg</div>
              <div class="text-xl font-semibold">
                <span v-if="averageScore !== null">{{
                  averageScore.toFixed(1)
                }}</span>
                <span v-else class="text-gray-400">N/A</span>
              </div>
            </div>

            <div class="p-3 rounded border">
              <div class="text-xs text-gray-500">Last 10 Avg</div>
              <div class="text-xl font-semibold">
                <span v-if="lastNAvg !== null">{{ lastNAvg.toFixed(1) }}</span>
                <span v-else class="text-gray-400">N/A</span>
              </div>

              <div v-if="scoreTrendMeta" class="text-[11px] mt-1">
                <el-tag
                  size="small"
                  :type="
                    scoreTrendMeta.direction === 'up'
                      ? 'success'
                      : scoreTrendMeta.direction === 'down'
                      ? 'danger'
                      : 'info'
                  "
                >
                  {{
                    scoreTrendMeta.direction === "up"
                      ? `Up (+${scoreTrendMeta.diff.toFixed(1)})`
                      : scoreTrendMeta.direction === "down"
                      ? `Down (${scoreTrendMeta.diff.toFixed(1)})`
                      : "Flat"
                  }}
                </el-tag>
              </div>
            </div>
          </div>

          <div class="p-3 rounded border">
            <div class="text-xs text-gray-500 mb-1">Performance Risk</div>
            <el-tag
              v-if="riskFlag"
              size="small"
              :type="
                riskFlag.level === 'high'
                  ? 'danger'
                  : riskFlag.level === 'medium'
                  ? 'warning'
                  : 'success'
              "
            >
              {{ riskFlag.label }}
            </el-tag>
            <span v-else class="text-gray-400 text-sm">N/A</span>
          </div>
        </el-card>

        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-2">Attendance Status Summary</div>
          <ClientOnly>
            <div class="w-full" style="height: 240px">
              <VChart
                :option="attendanceStatusOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[240px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>

        <el-card shadow="hover" class="mb-4" v-loading="loading">
          <div class="font-semibold mb-2">Score Trend</div>
          <ClientOnly>
            <div class="w-full" style="height: 240px">
              <VChart
                :option="scoreTrendOption"
                autoresize
                class="w-full h-full"
              />
            </div>
            <template #fallback>
              <div
                class="flex items-center justify-center h-[240px] text-xs text-gray-500"
              >
                Loading chart...
              </div>
            </template>
          </ClientOnly>
        </el-card>

        <el-card shadow="hover" v-loading="loading">
          <div class="font-semibold mb-2">Avg Score by Subject</div>
          <ClientOnly>
            <div class="w-full" style="height: 260px">
              <VChart
                :option="avgBySubjectOption"
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
  </div>
</template>

<style scoped></style>
