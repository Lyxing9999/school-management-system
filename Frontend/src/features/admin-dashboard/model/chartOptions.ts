import type { EChartsOption } from "echarts";

// Return `null` when no data; UI will show empty state.

export function buildAttendanceStatusOption(
  attendance: any
): EChartsOption | null {
  const data = attendance?.status_summary ?? [];
  if (!Array.isArray(data) || !data.length) return null;

  return {
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [
      {
        name: "Attendance",
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        data: data.map((row: any) => ({ name: row.status, value: row.count })),
      },
    ],
  };
}

export function buildAttendanceDailyTrendOption(
  attendance: any
): EChartsOption | null {
  const rows = attendance?.daily_trend ?? [];
  if (!Array.isArray(rows) || !rows.length) return null;

  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0 },
    grid: { top: 40, left: 40, right: 16, bottom: 40 },
    xAxis: { type: "category", data: rows.map((r: any) => r.date) },
    yAxis: { type: "value", minInterval: 1, name: "Records" },
    series: [
      {
        name: "Present",
        type: "line",
        smooth: true,
        data: rows.map((r: any) => r.present),
      },
      {
        name: "Absent",
        type: "line",
        smooth: true,
        data: rows.map((r: any) => r.absent),
      },
      {
        name: "Excused",
        type: "line",
        smooth: true,
        data: rows.map((r: any) => r.excused),
      },
    ],
  };
}

export function buildAttendanceByClassOption(
  attendance: any
): EChartsOption | null {
  const rows = attendance?.by_class ?? [];
  if (!Array.isArray(rows) || !rows.length) return null;

  const labels = rows.map((r: any) => r.class_name || r.class_id);

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
    yAxis: { type: "value", minInterval: 1, name: "Records" },
    series: [
      {
        name: "Present",
        type: "bar",
        stack: "total",
        data: rows.map((r: any) => r.present),
      },
      {
        name: "Absent",
        type: "bar",
        stack: "total",
        data: rows.map((r: any) => r.absent),
      },
      {
        name: "Excused",
        type: "bar",
        stack: "total",
        data: rows.map((r: any) => r.excused),
      },
    ],
  };
}

export function buildGradeAvgBySubjectOption(
  grades: any
): EChartsOption | null {
  const rows = grades?.avg_score_by_subject ?? [];
  if (!Array.isArray(rows) || !rows.length) return null;

  const labels = rows.map((r: any) => r.subject_name || r.subject_id);
  const values = rows.map((r: any) => r.avg_score);

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
    series: [{ name: "Average", type: "bar", data: values, barWidth: "60%" }],
  };
}

export function buildGradeDistributionOption(
  grades: any
): EChartsOption | null {
  const rows = grades?.grade_distribution ?? [];
  if (!Array.isArray(rows) || !rows.length) return null;

  return {
    tooltip: { trigger: "axis" },
    grid: { top: 40, left: 40, right: 16, bottom: 40 },
    xAxis: { type: "category", data: rows.map((r: any) => r.range) },
    yAxis: { type: "value", name: "Students", minInterval: 1 },
    series: [
      {
        name: "Students",
        type: "bar",
        data: rows.map((r: any) => r.count),
        barWidth: "50%",
      },
    ],
  };
}

export function buildPassRateByClassOption(grades: any): EChartsOption | null {
  const rows = grades?.pass_rate_by_class ?? [];
  if (!Array.isArray(rows) || !rows.length) return null;

  const labels = rows.map((r: any) => r.class_name || r.class_id);
  const rates = rows.map((r: any) =>
    Number((Number(r.pass_rate ?? 0) * 100).toFixed(1))
  );

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
    yAxis: { type: "value", name: "Pass rate (%)", min: 0, max: 100 },
    series: [{ name: "Pass rate", type: "bar", data: rates, barWidth: "60%" }],
  };
}

export function buildScheduleByWeekdayOption(
  schedule: any
): EChartsOption | null {
  const rows = schedule?.lessons_by_weekday ?? [];
  if (!Array.isArray(rows) || !rows.length) return null;

  return {
    tooltip: { trigger: "axis" },
    grid: { top: 40, left: 40, right: 16, bottom: 40 },
    xAxis: { type: "category", data: rows.map((r: any) => r.label) },
    yAxis: { type: "value", name: "Lessons", minInterval: 1 },
    series: [
      {
        name: "Lessons",
        type: "bar",
        data: rows.map((r: any) => r.lessons),
        barWidth: "50%",
      },
    ],
  };
}

export function buildScheduleByTeacherOption(
  schedule: any
): EChartsOption | null {
  const rows = schedule?.lessons_by_teacher ?? [];
  if (!Array.isArray(rows) || !rows.length) return null;

  const labels = rows.map((r: any) => r.teacher_name || r.teacher_id);
  const lessons = rows.map((r: any) => r.lessons);

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
    yAxis: { type: "value", name: "Lessons", minInterval: 1 },
    series: [{ name: "Lessons", type: "bar", data: lessons, barWidth: "60%" }],
  };
}
