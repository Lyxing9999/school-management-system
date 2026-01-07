// features/admin-dashboard/composables/useAdminDashboard.ts
import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { reportError } from "~/utils/errors/errors";
import { formatDate } from "~/utils/date/formatDate";

import type { AdminDashboardDTO } from "../api/dashboard.dto";
import { createDashboardService } from "../api/dashboard.client";
import {
  buildDashboardFilters,
  normalizeDateRange,
  type DateRange,
} from "../model/filters";

import { normalizeTopAbsentStudents } from "../model/normalize";
import {
  buildAttendanceStatusOption,
  buildAttendanceDailyTrendOption,
  buildAttendanceByClassOption,
  buildGradeAvgBySubjectOption,
  buildGradeDistributionOption,
  buildPassRateByClassOption,
  buildScheduleByWeekdayOption,
  buildScheduleByTeacherOption,
} from "../model/chartOptions";

function getErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof Error && err.message) return err.message;
  if (typeof err === "string") return err;
  return fallback;
}

export function useAdminDashboard() {
  const service = createDashboardService();

  const loading = ref(false);
  const errorMessage = ref<string | null>(null);
  const dashboard = ref<AdminDashboardDTO | null>(null);

  // defaults
  const defaultDateRange: DateRange = null;
  const filterDateRange = ref<DateRange>(defaultDateRange);

  function setDateRange(v: DateRange) {
    filterDateRange.value = normalizeDateRange(v);
  }

  const canReset = computed(() => filterDateRange.value !== null);

  async function resetFilters() {
    filterDateRange.value = defaultDateRange;
    await loadDashboard();
  }

  const loadingValue = computed(() => loading.value);
  const errorMessageValue = computed(() => errorMessage.value);
  const dateRangeValue = computed(() => filterDateRange.value);

  const overview = computed(() => dashboard.value?.overview);
  const attendance = computed(() => dashboard.value?.attendance);
  const grades = computed(() => dashboard.value?.grades);
  const schedule = computed(() => dashboard.value?.schedule);

  const totalStudents = computed(() => overview.value?.total_students ?? 0);
  const totalTeachers = computed(() => overview.value?.total_teachers ?? 0);
  const totalClasses = computed(() => overview.value?.total_classes ?? 0);
  const totalSubjects = computed(() => overview.value?.total_subjects ?? 0);

  const activeFilterLabel = computed(() => {
    if (!filterDateRange.value) return "Showing all available data";
    const [start, end] = filterDateRange.value;
    return `Date: ${formatDate(start.toISOString())} → ${formatDate(
      end.toISOString()
    )}`;
  });

  async function loadDashboard() {
    loading.value = true;
    errorMessage.value = null;

    try {
      const filters = buildDashboardFilters({
        dateRange: filterDateRange.value,
      });

      dashboard.value = await service.getDashboardData(filters, {
        showError: false,
      });
    } catch (err) {
      dashboard.value = null;
      reportError(err, "admin.dashboard.load", "log");

      const msg = getErrorMessage(err, "Failed to load admin dashboard data.");
      errorMessage.value = msg;
      ElMessage.error(msg);
    } finally {
      loading.value = false;
    }
  }

  const attendanceStatusOption = computed(() =>
    buildAttendanceStatusOption(attendance.value)
  );
  const attendanceDailyTrendOption = computed(() =>
    buildAttendanceDailyTrendOption(attendance.value)
  );
  const attendanceByClassOption = computed(() =>
    buildAttendanceByClassOption(attendance.value)
  );

  const gradeAvgBySubjectOption = computed(() =>
    buildGradeAvgBySubjectOption(grades.value)
  );
  const gradeDistributionOption = computed(() =>
    buildGradeDistributionOption(grades.value)
  );
  const passRateByClassOption = computed(() =>
    buildPassRateByClassOption(grades.value)
  );

  const scheduleByWeekdayOption = computed(() =>
    buildScheduleByWeekdayOption(schedule.value)
  );
  const scheduleByTeacherOption = computed(() =>
    buildScheduleByTeacherOption(schedule.value)
  );

  const topAbsentStudents = computed(() =>
    normalizeTopAbsentStudents(attendance.value?.top_absent_students)
  );
  const passRateRows = computed(() =>
    Array.isArray(grades.value?.pass_rate_by_class)
      ? grades.value!.pass_rate_by_class
      : []
  );
  const scheduleTeacherRows = computed(() =>
    Array.isArray(schedule.value?.lessons_by_teacher)
      ? schedule.value!.lessons_by_teacher
      : []
  );

  onMounted(loadDashboard);

  return {
    loadingValue,
    errorMessageValue,
    dateRangeValue,

    activeFilterLabel,
    canReset,
    setDateRange,
    loadDashboard,
    resetFilters,

    totalStudents,
    totalTeachers,
    totalClasses,
    totalSubjects,

    attendanceStatusOption,
    attendanceDailyTrendOption,
    attendanceByClassOption,
    gradeAvgBySubjectOption,
    gradeDistributionOption,
    passRateByClassOption,
    scheduleByWeekdayOption,
    scheduleByTeacherOption,

    topAbsentStudents,
    passRateRows,
    scheduleTeacherRows,
  };
}
