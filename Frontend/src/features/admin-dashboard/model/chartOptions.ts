import type { EChartsOption } from "echarts";

// Return `null` when no data; UI will show empty state.

const MANY_ROWS = 8;

function safeRows(raw: unknown): any[] {
  return Array.isArray(raw) ? raw : [];
}

function labelOf(value: unknown, fallback = "Unknown"): string {
  const text = String(value ?? fallback).trim();
  return text || fallback;
}

function shortLabel(value: unknown, max = 18): string {
  const text = labelOf(value);
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

function numberOf(value: unknown, fallback = 0): number {
  const n = Number(value ?? fallback);
  return Number.isFinite(n) ? n : fallback;
}

function percentOf(value: unknown): number {
  const raw = numberOf(value, 0);

  // Supports both 0.75 and 75.
  const percent = raw <= 1 ? raw * 100 : raw;

  return Number(percent.toFixed(1));
}

function commonTooltip(): EChartsOption["tooltip"] {
  return {
    trigger: "axis",
    axisPointer: { type: "shadow" },
  };
}

function verticalDataZoom(rowCount: number): EChartsOption["dataZoom"] {
  if (rowCount <= MANY_ROWS) return undefined;

  return [
    {
      type: "slider",
      yAxisIndex: 0,
      right: 4,
      width: 14,
      start: 0,
      end: Math.min(100, (MANY_ROWS / rowCount) * 100),
    },
    {
      type: "inside",
      yAxisIndex: 0,
    },
  ];
}

function horizontalDataZoom(rowCount: number): EChartsOption["dataZoom"] {
  if (rowCount <= MANY_ROWS) return undefined;

  return [
    {
      type: "slider",
      xAxisIndex: 0,
      bottom: 8,
      height: 18,
      start: 0,
      end: Math.min(100, (MANY_ROWS / rowCount) * 100),
    },
    {
      type: "inside",
      xAxisIndex: 0,
    },
  ];
}

function shouldUseHorizontal(rowCount: number): boolean {
  return rowCount > MANY_ROWS;
}

function buildManyCategoryBarOption(params: {
  title?: string;
  labels: string[];
  series: EChartsOption["series"];
  yAxisName?: string;
  xAxisName?: string;
  max?: number;
  percent?: boolean;
}): EChartsOption {
  const { labels, series, yAxisName, xAxisName, max, percent } = params;
  const horizontal = shouldUseHorizontal(labels.length);

  if (horizontal) {
    return {
      tooltip: commonTooltip(),
      legend: { top: 0, type: "scroll" },
      grid: { top: 44, left: 120, right: 36, bottom: 28 },
      dataZoom: verticalDataZoom(labels.length),
      xAxis: {
        type: "value",
        name: xAxisName,
        min: 0,
        max,
        axisLabel: percent ? { formatter: "{value}%" } : undefined,
      },
      yAxis: {
        type: "category",
        data: labels.map((x) => shortLabel(x, 22)),
        axisLabel: {
          fontSize: 11,
          overflow: "truncate",
        },
      },
      series,
    };
  }

  return {
    tooltip: commonTooltip(),
    legend: { top: 0, type: "scroll" },
    grid: { top: 44, left: 44, right: 16, bottom: labels.length > 4 ? 72 : 42 },
    dataZoom: horizontalDataZoom(labels.length),
    xAxis: {
      type: "category",
      data: labels,
      axisLabel: {
        interval: 0,
        rotate: labels.length > 4 ? 30 : 0,
        fontSize: 11,
        formatter: (value: string) => shortLabel(value, 12),
      },
    },
    yAxis: {
      type: "value",
      name: yAxisName,
      min: 0,
      max,
      minInterval: percent ? undefined : 1,
      axisLabel: percent ? { formatter: "{value}%" } : undefined,
    },
    series,
  };
}

export function buildAttendanceStatusOption(
  attendance: any,
): EChartsOption | null {
  const data = safeRows(attendance?.status_summary);
  if (!data.length) return null;

  return {
    tooltip: { trigger: "item" },
    legend: {
      bottom: 0,
      type: "scroll",
    },
    series: [
      {
        name: "Attendance",
        type: "pie",
        radius: ["42%", "68%"],
        center: ["50%", "45%"],
        avoidLabelOverlap: true,
        label: {
          formatter: "{b}: {d}%",
        },
        data: data.map((row: any) => ({
          name: labelOf(row.status),
          value: numberOf(row.count),
        })),
      },
    ],
  };
}

export function buildAttendanceDailyTrendOption(
  attendance: any,
): EChartsOption | null {
  const rows = safeRows(attendance?.daily_trend);
  if (!rows.length) return null;

  const labels = rows.map((r: any) => labelOf(r.date));

  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0, type: "scroll" },
    grid: {
      top: 44,
      left: 44,
      right: 16,
      bottom: rows.length > MANY_ROWS ? 64 : 40,
    },
    dataZoom: horizontalDataZoom(rows.length),
    xAxis: {
      type: "category",
      data: labels,
      axisLabel: {
        formatter: (value: string) => shortLabel(value, 10),
      },
    },
    yAxis: { type: "value", minInterval: 1, name: "Records" },
    series: [
      {
        name: "Present",
        type: "line",
        smooth: true,
        showSymbol: rows.length <= 14,
        data: rows.map((r: any) => numberOf(r.present)),
      },
      {
        name: "Absent",
        type: "line",
        smooth: true,
        showSymbol: rows.length <= 14,
        data: rows.map((r: any) => numberOf(r.absent)),
      },
      {
        name: "Excused",
        type: "line",
        smooth: true,
        showSymbol: rows.length <= 14,
        data: rows.map((r: any) => numberOf(r.excused)),
      },
    ],
  };
}

export function buildAttendanceByClassOption(
  attendance: any,
): EChartsOption | null {
  const rows = safeRows(attendance?.by_class);
  if (!rows.length) return null;

  const labels = rows.map((r: any) => labelOf(r.class_name || r.class_id));

  return buildManyCategoryBarOption({
    labels,
    xAxisName: "Records",
    yAxisName: "Records",
    series: [
      {
        name: "Present",
        type: "bar",
        stack: "total",
        emphasis: { focus: "series" },
        data: rows.map((r: any) => numberOf(r.present)),
      },
      {
        name: "Absent",
        type: "bar",
        stack: "total",
        emphasis: { focus: "series" },
        data: rows.map((r: any) => numberOf(r.absent)),
      },
      {
        name: "Excused",
        type: "bar",
        stack: "total",
        emphasis: { focus: "series" },
        data: rows.map((r: any) => numberOf(r.excused)),
      },
    ],
  });
}

export function buildGradeAvgBySubjectOption(
  grades: any,
): EChartsOption | null {
  const rows = safeRows(grades?.avg_score_by_subject);
  if (!rows.length) return null;

  const labels = rows.map((r: any) => labelOf(r.subject_name || r.subject_id));

  return buildManyCategoryBarOption({
    labels,
    xAxisName: "Avg score",
    yAxisName: "Avg score",
    max: 100,
    series: [
      {
        name: "Average",
        type: "bar",
        data: rows.map((r: any) => numberOf(r.avg_score)),
        barMaxWidth: 36,
      },
    ],
  });
}

export function buildGradeDistributionOption(
  grades: any,
): EChartsOption | null {
  const rows = safeRows(grades?.grade_distribution);
  if (!rows.length) return null;

  return {
    tooltip: commonTooltip(),
    grid: { top: 40, left: 44, right: 16, bottom: 40 },
    xAxis: {
      type: "category",
      data: rows.map((r: any) => labelOf(r.range)),
    },
    yAxis: { type: "value", name: "Students", minInterval: 1 },
    series: [
      {
        name: "Students",
        type: "bar",
        data: rows.map((r: any) => numberOf(r.count)),
        barMaxWidth: 36,
      },
    ],
  };
}

export function buildPassRateByClassOption(grades: any): EChartsOption | null {
  const rows = safeRows(grades?.pass_rate_by_class);
  if (!rows.length) return null;

  const labels = rows.map((r: any) => labelOf(r.class_name || r.class_id));
  const rates = rows.map((r: any) => percentOf(r.pass_rate));

  return buildManyCategoryBarOption({
    labels,
    xAxisName: "Pass rate",
    yAxisName: "Pass rate",
    max: 100,
    percent: true,
    series: [
      {
        name: "Pass rate",
        type: "bar",
        data: rates,
        barMaxWidth: 34,
        label: {
          show: rows.length <= MANY_ROWS,
          position: shouldUseHorizontal(rows.length) ? "right" : "top",
          formatter: "{c}%",
        },
      },
    ],
  });
}

export function buildScheduleByWeekdayOption(
  schedule: any,
): EChartsOption | null {
  const rows = safeRows(schedule?.lessons_by_weekday);
  if (!rows.length) return null;

  return {
    tooltip: commonTooltip(),
    grid: { top: 40, left: 44, right: 16, bottom: 40 },
    xAxis: { type: "category", data: rows.map((r: any) => labelOf(r.label)) },
    yAxis: { type: "value", name: "Lessons", minInterval: 1 },
    series: [
      {
        name: "Lessons",
        type: "bar",
        data: rows.map((r: any) => numberOf(r.lessons)),
        barMaxWidth: 36,
      },
    ],
  };
}

export function buildScheduleByTeacherOption(
  schedule: any,
): EChartsOption | null {
  const rows = safeRows(schedule?.lessons_by_teacher);
  if (!rows.length) return null;

  const labels = rows.map((r: any) => labelOf(r.teacher_name || r.teacher_id));

  return buildManyCategoryBarOption({
    labels,
    xAxisName: "Lessons",
    yAxisName: "Lessons",
    series: [
      {
        name: "Lessons",
        type: "bar",
        data: rows.map((r: any) => numberOf(r.lessons)),
        barMaxWidth: 34,
      },
    ],
  });
}
