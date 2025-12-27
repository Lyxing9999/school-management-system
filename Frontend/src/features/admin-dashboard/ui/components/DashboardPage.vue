<script setup lang="ts">
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";
import { useAdminDashboard } from "~/features/admin-dashboard/composables/useAdminDashboard";

import DashboardFilters from "../components/DashboardFilters.vue";
import KpiCard from "../components/KpiCard.vue";

import AttendanceSection from "../sections/AttendanceSection.vue";
import GradesSection from "../sections/GradesSection.vue";
import ScheduleSection from "../sections/ScheduleSection.vue";

const vm = useAdminDashboard();
</script>

<template>
  <div class="p-4 space-y-4">
    <OverviewHeader
      title="Admin Dashboard"
      description="High-level overview of attendance, grades, and schedule across the school."
      :loading="vm.loadingValue.value"
      :showRefresh="false"
    >
      <template #icon>
        <span
          class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-[var(--color-primary-light-6)] text-[color:var(--color-primary)] border border-[color:var(--color-primary-light-4)]"
        >
          {{ vm.activeFilterLabel }}
        </span>
      </template>

      <template #actions>
        <DashboardFilters
          :date-range="vm.dateRangeValue.value"
          :term="vm.termValue.value"
          :term-options="vm.termOptions"
          :loading="vm.loadingValue.value"
          @update:dateRange="vm.setDateRange"
          @update:term="vm.setTerm"
          @apply="vm.loadDashboard"
        />
      </template>
    </OverviewHeader>

    <el-alert
      v-if="vm.errorMessageValue.value"
      :title="vm.errorMessageValue.value || ''"
      type="error"
      show-icon
      class="mb-2"
    />

    <el-row :gutter="16">
      <el-col :xs="12" :sm="6">
        <KpiCard label="Total students" :value="vm.totalStudents.value" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <KpiCard label="Total teachers" :value="vm.totalTeachers.value" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <KpiCard label="Total classes" :value="vm.totalClasses.value" />
      </el-col>
      <el-col :xs="12" :sm="6">
        <KpiCard label="Total subjects" :value="vm.totalSubjects.value" />
      </el-col>
    </el-row>

    <AttendanceSection
      :loading="vm.loadingValue.value"
      :status-option="vm.attendanceStatusOption.value"
      :daily-trend-option="vm.attendanceDailyTrendOption.value"
      :by-class-option="vm.attendanceByClassOption.value"
      :top-absent-students="vm.topAbsentStudents.value"
    />

    <GradesSection
      :loading="vm.loadingValue.value"
      :avg-by-subject-option="vm.gradeAvgBySubjectOption.value"
      :distribution-option="vm.gradeDistributionOption.value"
      :pass-rate-option="vm.passRateByClassOption.value"
      :pass-rate-rows="vm.passRateRows.value"
    />
    <ScheduleSection
      :loading="vm.loadingValue.value"
      :by-weekday-option="vm.scheduleByWeekdayOption.value"
      :by-teacher-option="vm.scheduleByTeacherOption.value"
      :schedule-teacher-rows="vm.scheduleTeacherRows.value"
    />
  </div>
</template>
