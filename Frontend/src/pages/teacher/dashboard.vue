<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";

definePageMeta({ layout: "default" });

import { teacherService } from "~/api/teacher";
import { formatDate } from "~/utils/date/formatDate";

import type {
  ClassSectionDTO,
  GradeDTO,
  AttendanceDTO,
} from "~/api/types/school.dto";

import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";

import type {
  TeacherClassListWithSummeryDTO,
  TeacherScheduleDTO,
  TeacherScheduleListDTO,
} from "~/api/teacher/dto";

import { reportError } from "~/utils/errors/errors";

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
  record_date: string; // normalized alias
};

type TeacherScheduleItem = TeacherScheduleDTO;

type ClassSummary = {
  total_classes: number;
  total_students: number;
  total_subjects: number;
};

/* ------------------------------------------------
 * State
 * ------------------------------------------------ */

const loadingOverview = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<TeacherClassEnriched[]>([]);
const classSummary = ref<ClassSummary | null>(null);

const grades = ref<TeacherGradeEnriched[]>([]);
const schedule = ref<TeacherScheduleItem[]>([]);
const attendance = ref<TeacherAttendanceEnriched[]>([]);

const focusClassId = ref<string | null>(null);
const attendanceLoading = ref(false);

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
 * Robust unwrap for:
 * - ApiResponse<T>                    => { success, message, data }
 * - axios { data: ApiResponse<T> }    => { data: { success, message, data } }
 * - axios { data: T }                 => { data: T }
 * - already T
 */
function unwrapData<T>(res: any): T | null {
  if (!res) return null;

  // ApiResponse<T>
  if (
    typeof res === "object" &&
    res !== null &&
    "success" in res &&
    "data" in res
  ) {
    return res.data as T;
  }

  // axios { data: ApiResponse<T> }
  if (
    typeof res === "object" &&
    res !== null &&
    res.data &&
    typeof res.data === "object" &&
    "success" in res.data &&
    "data" in res.data
  ) {
    return res.data.data as T;
  }

  // axios { data: T }
  if (typeof res === "object" && res !== null && "data" in res) {
    return res.data as T;
  }

  // already T
  return res as T;
}

function getItems<T>(res: any): T[] {
  const payload = unwrapData<any>(res);
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload.items)) return payload.items as T[];
  return [];
}

/**
 * Backend caps page_size at 100 -> dashboard must fetch all pages.
 * Supports optional class_id/day/time filters if backend provides them.
 */
async function fetchAllMySchedule(opts?: {
  class_id?: string;
  day_of_week?: number;
  start_time_from?: string; // "HH:mm"
  start_time_to?: string; // "HH:mm"
  signal?: AbortSignal;
}): Promise<TeacherScheduleDTO[]> {
  const page_size = 100;
  let page = 1;

  const all: TeacherScheduleDTO[] = [];

  while (true) {
    const res = await teacher.teacher.listMySchedule(
      {
        page,
        page_size,
        class_id: opts?.class_id,
        day_of_week: opts?.day_of_week,
        start_time_from: opts?.start_time_from,
        start_time_to: opts?.start_time_to,
        signal: opts?.signal,
      } as any,
      { showError: false } as any
    );

    const payload = unwrapData<TeacherScheduleListDTO>(res);

    const items = (payload?.items ?? []) as TeacherScheduleDTO[];
    const total = Number(payload?.total ?? items.length);

    all.push(...items);

    if (items.length === 0) break;
    if (all.length >= total) break;

    page += 1;
  }

  return all;
}

/* ------------------------------------------------
 * Load data
 * ------------------------------------------------ */

const loadClassDetails = async (classId: string) => {
  try {
    const [gradesRes, attendanceRes] = await Promise.all([
      teacher.teacher.listGradesForClass(classId, { showError: false } as any),
      teacher.teacher.listAttendanceForClass(classId, {
        showError: false,
      } as any),
    ]);

    grades.value = getItems<TeacherGradeEnriched>(gradesRes);

    const raw = getItems<any>(attendanceRes);
    attendance.value = raw.map((a: any) => ({
      ...a,
      record_date: String(a.record_date ?? a.date ?? ""),
    })) as TeacherAttendanceEnriched[];
  } catch (err) {
    reportError(err, `teacher.classDetails.load classId=${classId}`, "log");
    ElMessage.error(extractErrorMessage(err, "Failed to load class details."));
  }
};

const loadOverview = async () => {
  loadingOverview.value = true;
  errorMessage.value = null;

  try {
    // fetch classes summary + schedule in parallel
    const [classesResSummery, scheduleAll] = await Promise.all([
      teacher.teacher.listMyClassesWithSummery({ showError: false } as any),
      fetchAllMySchedule(),
    ]);

    const classPayload = unwrapData<TeacherClassListWithSummeryDTO>(
      classesResSummery
    ) ?? {
      items: [],
      summary: undefined,
    };

    classes.value = (classPayload.items as TeacherClassEnriched[]) ?? [];
    classSummary.value =
      (classPayload.summary as ClassSummary | undefined) ?? null;

    // set schedule (for charts + today lessons)
    schedule.value = scheduleAll;

    // Default focus class
    if (!focusClassId.value && classes.value.length > 0) {
      focusClassId.value = classes.value[0].id;
    }

    // focus class details
    if (focusClassId.value) {
      await loadClassDetails(focusClassId.value);
    } else {
      grades.value = [];
      attendance.value = [];
    }
  } catch (err: unknown) {
    reportError(err, "teacher.dashboard.loadOverview", "log");
    errorMessage.value = extractErrorMessage(
      err,
      "Failed to load teacher dashboard data."
    );
  } finally {
    loadingOverview.value = false;
  }
};

const onFocusClassChange = async (value: string) => {
  if (!value) return;
  attendanceLoading.value = true;
  try {
    await loadClassDetails(value);

    // Optional: if you want charts to reflect focus class schedule via backend filters:
    // schedule.value = await fetchAllMySchedule({ class_id: value });
  } finally {
    attendanceLoading.value = false;
  }
};

/* ------------------------------------------------
 * Computed
 * ------------------------------------------------ */

const focusClassName = computed(() => {
  if (!focusClassId.value) return null;
  return classes.value.find((c) => c.id === focusClassId.value)?.name ?? null;
});

const totalClasses = computed(() => {
  if (classSummary.value) return classSummary.value.total_classes;
  return classes.value.length;
});

const totalStudents = computed(() => {
  if (classSummary.value) return classSummary.value.total_students;

  return classes.value.reduce((sum, c) => {
    if (typeof c.student_count === "number") return sum + c.student_count;
    if (Array.isArray((c as any).student_ids))
      return sum + (c as any).student_ids.length;
    return sum;
  }, 0);
});

const totalSubjects = computed(() => {
  if (classSummary.value) return classSummary.value.total_subjects;

  return classes.value.reduce((sum, c) => {
    if (typeof c.subject_count === "number") return sum + c.subject_count;
    if (Array.isArray((c as any).subject_ids))
      return sum + (c as any).subject_ids.length;
    return sum;
  }, 0);
});

// backend uses 1=Mon..7=Sun
const todayDayOfWeek = computed(() => {
  const jsDay = new Date().getDay(); // 0=Sun..6=Sat
  return jsDay === 0 ? 7 : jsDay;
});

const todaySchedule = computed(() =>
  schedule.value.filter((s) => Number(s.day_of_week) === todayDayOfWeek.value)
);

const recentAttendance = computed(() =>
  attendance.value
    .slice()
    .sort((a, b) => {
      const ad = new Date(a.record_date || 0).getTime();
      const bd = new Date(b.record_date || 0).getTime();
      return bd - ad;
    })
    .slice(0, 8)
);

/* ------------------------------------------------
 * Charts
 * ------------------------------------------------ */

const scheduleByDayOption = computed(() => {
  // if schedule items contain class_id and focus selected -> filter
  const hasClassId = schedule.value.some((s) => !!(s as any).class_id);

  const filteredSchedule =
    focusClassId.value && hasClassId
      ? schedule.value.filter((s) => (s as any).class_id === focusClassId.value)
      : schedule.value;

  const counts: number[] = [];
  for (let day = 1; day <= 7; day++) {
    counts.push(
      filteredSchedule.filter((s) => Number(s.day_of_week) === day).length
    );
  }

  return {
    tooltip: { trigger: "axis" },
    grid: { top: 24, left: 40, right: 16, bottom: 40 },
    xAxis: {
      type: "category",
      data: weekdayShortLabels,
      axisTick: { alignWithLabel: true },
    },
    yAxis: { type: "value", minInterval: 1, name: "Lessons" },
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

const gradeBySubjectOption = computed(() => {
  if (!grades.value.length) {
    return {
      title: { text: "No grade data yet", left: "center", top: "center" },
    };
  }

  const map = new Map<string, { total: number; count: number }>();
  for (const g of grades.value) {
    const key = g.subject_label || "Unknown subject";
    const prev = map.get(key) ?? { total: 0, count: 0 };
    const score = Number(g.score ?? 0);
    prev.total += score;
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
    yAxis: { type: "value", min: 0, max: 100, name: "Avg score" },
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

const attendanceStatusOption = computed(() => {
  if (!attendance.value.length) {
    return {
      title: { text: "No attendance data yet", left: "center", top: "center" },
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
    series: [{ name: "Attendance", type: "pie", radius: ["40%", "70%"], data }],
  };
});

const gradeDistributionOption = computed(() => {
  if (!grades.value.length) {
    return {
      title: { text: "No grade data yet", left: "center", top: "center" },
    };
  }

  const buckets = [
    { label: "0–49", min: 0, max: 49 },
    { label: "50–59", min: 50, max: 59 },
    { label: "60–69", min: 60, max: 69 },
    { label: "70–79", min: 70, max: 79 },
    { label: "80–89", min: 80, max: 89 },
    { label: "90–100", min: 90, max: 100 },
  ];

  const counts = buckets.map(
    (b) =>
      grades.value.filter((g) => {
        const score = Number(g.score ?? 0);
        return score >= b.min && score <= b.max;
      }).length
  );

  return {
    tooltip: {
      trigger: "axis",
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params;
        return `${p.axisValue}<br/>Students: ${p.data}`;
      },
    },
    grid: { top: 24, left: 40, right: 16, bottom: 40 },
    xAxis: { type: "category", data: buckets.map((b) => b.label) },
    yAxis: { type: "value", minInterval: 1, name: "Students" },
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

/* ------------------------------------------------
 * Lifecycle
 * ------------------------------------------------ */

onMounted(async () => {
  await loadOverview();
});
</script>

<template>
  <div class="p-4 space-y-4">
    <OverviewHeader
      title="Teacher Dashboard"
      description="Overview of your overall classes plus detailed performance and attendance for your focus class."
      :loading="loadingOverview"
      :showRefresh="false"
    >
      <template #icon>
        <span
          v-if="focusClassName"
          class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-[var(--color-primary-light-6)] text-[color:var(--color-primary)] border border-[color:var(--color-primary-light-4)]"
        >
          Focus: {{ focusClassName }}
        </span>
      </template>

      <template #custom-stats>
        <p v-if="!focusClassName" class="text-[11px] text-gray-500 mt-1">
          Assign a class to see focus grades and attendance here.
        </p>
      </template>

      <template #actions>
        <div class="flex items-center gap-2">
          <el-select
            v-model="focusClassId"
            placeholder="Select class"
            size="small"
            style="min-width: 180px"
            @change="onFocusClassChange"
            :disabled="classes.length === 0"
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
            :loading="loadingOverview"
            class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
            @click="loadOverview"
          >
            Refresh
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

    <!-- Stats -->
    <el-row :gutter="16">
      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500">Classes you teach</div>
          <div class="text-2xl font-semibold mt-1">{{ totalClasses }}</div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500">Total students</div>
          <div class="text-2xl font-semibold mt-1">{{ totalStudents }}</div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500">Subjects taught</div>
          <div class="text-2xl font-semibold mt-1">{{ totalSubjects }}</div>
        </el-card>
      </el-col>

      <el-col :xs="12" :sm="6" :md="6" :lg="6">
        <el-card shadow="hover">
          <div class="text-xs text-gray-500">Today&apos;s Lessons</div>
          <div class="text-2xl font-semibold mt-1">
            {{ todaySchedule.length }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts -->
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loadingOverview" class="mb-4">
          <div class="mb-2">
            <div class="font-semibold">Teaching Schedule Overview</div>
            <div class="text-xs text-gray-500">
              Lessons per weekday for the focus class (or all classes if
              class_id is not available).
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
          <div class="mb-2">
            <div class="font-semibold">Grade Overview (focus class)</div>
            <div class="text-xs text-gray-500">
              Average score per subject in your focus class.
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

    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loadingOverview" class="mb-4">
          <div class="mb-2">
            <div class="font-semibold">Attendance Overview (focus class)</div>
            <div class="text-xs text-gray-500">
              Distribution of present, absent, and excused records in the focus
              class.
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
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="loadingOverview" class="mb-4">
          <div class="mb-2">
            <div class="font-semibold">Score Distribution (focus class)</div>
            <div class="text-xs text-gray-500">
              How many students fall into each score range.
            </div>
          </div>

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

    <!-- Recent Attendance -->
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
            v-loading="attendanceLoading || loadingOverview"
            size="small"
            style="width: 100%"
            :height="320"
            border
          >
            <el-table-column label="Date" min-width="130">
              <template #default="{ row }">
                {{ formatDate(row.record_date || row.date) }}
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
              prop="lifecycle.created_at"
              label="Recorded At"
              min-width="180"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                {{ formatDate(row.lifecycle?.created_at) }}
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
