import { ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { reportError } from "~/utils/errors";
import { formatDate } from "~/utils/formatDate";

import type { AdminDashboardDTO } from "../api/dashboard.dto";
import { createDashboardService } from "../api/dashboard.client";
import {
  buildDashboardFilters,
  termOptions,
  type DateRange,
  type TermValue,
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

  const filterDateRange = ref<DateRange>(null);
  const filterTerm = ref<TermValue>("");

  function setDateRange(v: DateRange) {
    filterDateRange.value = v;
  }
  function setTerm(v: TermValue) {
    filterTerm.value = v;
  }

  const loadingValue = computed(() => loading.value);
  const errorMessageValue = computed(() => errorMessage.value);
  const dateRangeValue = computed(() => filterDateRange.value);
  const termValue = computed(() => filterTerm.value);

  const overview = computed(() => dashboard.value?.overview);
  const attendance = computed(() => dashboard.value?.attendance);
  const grades = computed(() => dashboard.value?.grades);
  const schedule = computed(() => dashboard.value?.schedule);

  const totalStudents = computed(() => overview.value?.total_students ?? 0);
  const totalTeachers = computed(() => overview.value?.total_teachers ?? 0);
  const totalClasses = computed(() => overview.value?.total_classes ?? 0);
  const totalSubjects = computed(() => overview.value?.total_subjects ?? 0);

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
      const label =
        termOptions.find((t) => t.value === filterTerm.value)?.label ??
        `Term: ${filterTerm.value}`;
      parts.push(label);
    }

    return parts.length ? parts.join(" • ") : "Showing all available data";
  });

  async function loadDashboard() {
    loading.value = true;
    errorMessage.value = null;

    try {
      const filters = buildDashboardFilters({
        dateRange: filterDateRange.value,
        term: filterTerm.value,
      });

      // IMPORTANT: always returns plain JSON from axios
      dashboard.value = await service.getDashboardData(filters, {
        showError: false, // avoid duplicate ElMessage if you want
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

  // chart options (plain objects)
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

  // arrays hardened
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
    termValue,

    termOptions,
    activeFilterLabel,
    setDateRange,
    setTerm,
    loadDashboard,

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
