<script setup lang="ts">
import {
  Money,
  Document,
  Clock,
  Timer,
  TrendCharts,
} from "@element-plus/icons-vue";
import PrototypePageShell from "~/components/hrms/PrototypePageShell.vue";
import { ROUTES } from "~/constants/routes";

const stats = [
  {
    label: "Payroll Runs",
    value: "Generate",
    hint: "Build monthly payroll batches",
  },
  { label: "Payslips", value: "Ready", hint: "Publish payroll outputs" },
  {
    label: "Attendance Final",
    value: "Import",
    hint: "Use finalized attendance data",
  },
  {
    label: "OT Approved",
    value: "Included",
    hint: "Payroll accepts approved overtime",
  },
];

const actions = [
  {
    title: "Generate Payroll",
    description: "Start a payroll batch for the current cycle.",
    route: ROUTES.PAYROLL_MANAGER.PAYROLL_GENERATE,
    icon: Money,
    color: "var(--button-success-bg)",
  },
  {
    title: "Payroll Runs",
    description: "Inspect generated payroll runs and statuses.",
    route: ROUTES.PAYROLL_MANAGER.PAYROLL_RUNS,
    icon: TrendCharts,
    color: "var(--chart-6)",
  },
  {
    title: "Payslips",
    description: "Open the employee payslip publishing view.",
    route: ROUTES.PAYROLL_MANAGER.PAYSLIPS,
    icon: Document,
    color: "var(--button-warning-bg)",
  },
  {
    title: "Attendance Final",
    description: "Review finalized attendance before pay calculation.",
    route: ROUTES.PAYROLL_MANAGER.ATTENDANCE_FINAL,
    icon: Clock,
    color: "var(--chart-7)",
  },
  {
    title: "Approved Overtime",
    description: "Bring approved overtime into payroll calculations.",
    route: ROUTES.PAYROLL_MANAGER.OVERTIME_APPROVED,
    icon: Timer,
    color: "var(--button-success-bg)",
  },
  {
    title: "Payroll Reports",
    description: "Open payroll summaries and reporting routes.",
    route: ROUTES.PAYROLL_MANAGER.REPORTS_PAYROLL,
    icon: Document,
    color: "var(--muted-color)",
  },
];

const sections = [
  {
    title: "Backend payroll flow",
    items: [
      "Final attendance is the payroll input",
      "Approved overtime is included in the calculation",
      "Payroll generation produces run history and payslip data",
    ],
  },
  {
    title: "Workspace scope",
    items: [
      "Generate payroll",
      "Review run history",
      "Publish payslips",
      "Inspect reports",
    ],
    note: "Payroll manager end-to-end workflow",
  },
];
</script>

<template>
  <PrototypePageShell
    title="Payroll Workspace"
    description="Payroll landing page for payroll managers. It mirrors the backend payroll pipeline and exposes the core review routes."
    badge="Payroll"
    accent="var(--button-success-bg)"
    :stats="stats"
    :actions="actions"
    :sections="sections"
  />
</template>
