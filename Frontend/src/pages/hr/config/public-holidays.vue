<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useNuxtApp } from "nuxt/app";
import { ElMessageBox } from "element-plus";
import {
  ArrowLeftBold,
  ArrowRightBold,
  Delete,
  Edit,
  Plus,
  Refresh,
  RefreshLeft,
  Search,
  Upload,
} from "@element-plus/icons-vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import type { ColumnConfig } from "~/components/types/tableEdit";
import type {
  PublicHolidayDTO,
  PublicHolidayCreateDTO,
  PublicHolidayUpdateDTO,
  PublicHolidayImportResultDTO,
} from "~/api/hr_admin/publicHoliday";
import { displayRelation } from "~/api/hr_admin/shared/displayRelation";

type HolidayFilter = "active" | "deleted" | "all";

interface HolidayFormModel {
  name: string;
  name_kh: string | null;
  date: string; // YYYY-MM-DD
  is_paid: boolean;
  description: string | null;
}

import { hrmsAdminService } from "~/api/hr_admin";

const publicHolidayService = hrmsAdminService().publicHoliday;

const holidays = ref<PublicHolidayDTO[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const dialogMode = ref<"create" | "edit">("create");
const saving = ref(false);
const actionLoading = ref<Record<string, boolean>>({});
const currentHolidayId = ref<string>("");
const initialFormValues = ref<HolidayFormModel | null>(null);

const q = ref("");
const filter = ref<HolidayFilter>("active");
const page = ref(1);
const pageSize = ref(10);
const selectedYear = ref<number | null>(null);
const viewMode = ref<"table" | "calendar">("table");
const currentCalendarDate = ref(new Date());
const selectedCalendarDateHolidays = ref<PublicHolidayDTO[]>([]);
const calendarSummaryVisible = ref(false);
const importingDefaults = ref(false);
const importYear = ref(new Date().getFullYear());
const importSummaryVisible = ref(false);
const importSummary = ref<PublicHolidayImportResultDTO | null>(null);
const checkByDate = ref(toLocalDateKey(new Date()));
const checkingByDate = ref(false);
const byDateChecked = ref(false);
const byDateResult = ref<PublicHolidayDTO | null>(null);

function toLocalDateKey(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getDateKeyFromBackend(value: string): string {
  const firstTenChars = value.slice(0, 10);
  if (/^\d{4}-\d{2}-\d{2}$/.test(firstTenChars)) {
    return firstTenChars;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return toLocalDateKey(parsed);
}

function parseHolidayDate(value: string): Date {
  const dateKey = getDateKeyFromBackend(value);
  const match = dateKey.match(/^(\d{4})-(\d{2})-(\d{2})$/);

  if (!match) {
    return new Date(value);
  }

  const [, year, month, day] = match;
  // Noon avoids timezone boundary issues when comparing local calendar dates.
  return new Date(Number(year), Number(month) - 1, Number(day), 12, 0, 0, 0);
}

const form = reactive<HolidayFormModel>(getDefaultForm());

const tableColumns: ColumnConfig<PublicHolidayDTO>[] = [
  {
    field: "name",
    label: "Holiday Name",
    minWidth: "200px",
  },
  {
    field: "name_kh",
    label: "ឈ្មោះក្នុងខ្មែរ",
    minWidth: "200px",
    useSlot: true,
    slotName: "name_kh",
  },
  {
    field: "date",
    label: "Date",
    width: "140px",
    useSlot: true,
    slotName: "date",
  },
  {
    field: "is_paid",
    label: "Paid",
    width: "100px",
    useSlot: true,
    slotName: "paid_status",
  },
  {
    field: "description",
    label: "Description",
    minWidth: "200px",
    useSlot: true,
    slotName: "description",
  },
  {
    field: "lifecycle",
    label: "Updated",
    minWidth: "180px",
    useSlot: true,
    slotName: "updated_at",
  },
  {
    field: "id",
    label: "Actions",
    operation: true,
    minWidth: "200px",
    fixed: "right",
    useSlot: true,
    slotName: "operation",
  },
];

const summaryCards = computed(() => {
  const active = holidays.value.filter((item) => !item.lifecycle?.deleted_at);
  const deleted = holidays.value.filter((item) => item.lifecycle?.deleted_at);
  const paid = active.filter((item) => item.is_paid);
  const currentYear = new Date().getFullYear();
  const thisYear = active.filter(
    (item) => parseHolidayDate(item.date).getFullYear() === currentYear,
  );

  return [
    { label: "Total holidays", value: holidays.value.length },
    { label: "Active holidays", value: active.length },
    { label: "Paid holidays", value: paid.length },
    { label: "This year", value: thisYear.length },
    { label: "Deleted", value: deleted.length },
  ];
});

const filteredHolidays = computed(() => {
  const keyword = q.value.trim().toLowerCase();

  return holidays.value
    .filter((item) => {
      const isDeleted = Boolean(item.lifecycle?.deleted_at);
      if (filter.value === "active" && isDeleted) return false;
      if (filter.value === "deleted" && !isDeleted) return false;

      // Filter by year if selected
      if (selectedYear.value) {
        const itemYear = parseHolidayDate(item.date).getFullYear();
        if (itemYear !== selectedYear.value) return false;
      }

      if (!keyword) return true;

      // Search across multiple fields
      const searchableText = [
        item.name,
        item.name_kh,
        item.date,
        item.description,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return searchableText.includes(keyword);
    })
    .sort(
      (a, b) =>
        parseHolidayDate(a.date).getTime() - parseHolidayDate(b.date).getTime(),
    );
});

const totalRows = computed(() => filteredHolidays.value.length);

const pagedHolidays = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  return filteredHolidays.value.slice(start, start + pageSize.value);
});

const availableYears = computed(() => {
  const years = new Set<number>();
  const currentYear = new Date().getFullYear();

  // Add current year and next 5 years
  for (let i = 0; i <= 5; i++) {
    years.add(currentYear + i);
  }

  // Add years from existing holidays
  holidays.value.forEach((holiday) => {
    years.add(parseHolidayDate(holiday.date).getFullYear());
  });

  return Array.from(years).sort((a, b) => b - a);
});

const formError = computed(() => {
  // Name validation
  if (!form.name.trim()) return "Holiday name is required.";
  if (form.name.trim().length < 2)
    return "Holiday name must be at least 2 characters.";
  if (form.name.trim().length > 100)
    return "Holiday name cannot exceed 100 characters.";

  // Name KH validation
  if (form.name_kh && form.name_kh.trim().length > 100)
    return "Khmer name cannot exceed 100 characters.";

  // Date validation
  if (!form.date) return "Date is required.";

  const selectedDate = parseHolidayDate(form.date);
  if (Number.isNaN(selectedDate.getTime())) return "Invalid date.";

  // Description validation
  if (form.description && form.description.length > 500)
    return "Description cannot exceed 500 characters.";

  return "";
});

const hasFormChanged = computed(() => {
  if (!initialFormValues.value) return false;
  return JSON.stringify(form) !== JSON.stringify(initialFormValues.value);
});

const canSubmitForm = computed(() => {
  if (formError.value) return false;
  return dialogMode.value === "create" ? true : hasFormChanged.value;
});

// Calendar computed properties
const activeHolidaysOnly = computed(() => {
  return holidays.value.filter((item) => !item.lifecycle?.deleted_at);
});

const calendarYear = computed(() => currentCalendarDate.value.getFullYear());
const calendarMonth = computed(() => currentCalendarDate.value.getMonth());
const todayDateStr = computed(() => toLocalDateKey(new Date()));

const holidaysByDate = computed(() => {
  const map = new Map<string, PublicHolidayDTO[]>();
  activeHolidaysOnly.value
    .filter(
      (holiday) =>
        parseHolidayDate(holiday.date).getFullYear() === calendarYear.value &&
        parseHolidayDate(holiday.date).getMonth() === calendarMonth.value,
    )
    .forEach((holiday) => {
      const key = getDateKeyFromBackend(holiday.date);
      if (!map.has(key)) {
        map.set(key, []);
      }
      map.get(key)!.push(holiday);
    });
  return map;
});

const calendarDays = computed(() => {
  const firstDay = new Date(calendarYear.value, calendarMonth.value, 1);
  const lastDay = new Date(calendarYear.value, calendarMonth.value + 1, 0);
  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - firstDay.getDay());

  const days = [];
  const current = new Date(startDate);

  while (current <= lastDay || current.getDay() !== 0) {
    const dateStr = toLocalDateKey(current);
    const hasHoliday = holidaysByDate.value.has(dateStr);
    const holidaysOnDate = holidaysByDate.value.get(dateStr) || [];

    days.push({
      date: new Date(current),
      dateStr,
      isCurrentMonth: current.getMonth() === calendarMonth.value,
      hasHoliday,
      holidayCount: holidaysOnDate.length,
      isToday: dateStr === todayDateStr.value,
      holidays: holidaysOnDate,
    });

    current.setDate(current.getDate() + 1);
  }

  return days;
});

const monthYear = computed(() => {
  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  return `${monthNames[calendarMonth.value]} ${calendarYear.value}`;
});

const calendarSummaryTitle = computed(() => {
  const holidayCount = selectedCalendarDateHolidays.value.length;
  const baseDate = selectedCalendarDateHolidays.value[0]?.date || "";
  return `Holiday${holidayCount > 1 ? "s" : ""} on ${formatDate(baseDate)}`;
});

function getDefaultForm(): HolidayFormModel {
  return {
    name: "",
    name_kh: null,
    date: toLocalDateKey(new Date()),
    is_paid: true,
    description: null,
  };
}

function resetForm() {
  Object.assign(form, getDefaultForm());
  initialFormValues.value = null;
}

function fillForm(holiday: PublicHolidayDTO) {
  const normalized = {
    name: holiday.name,
    name_kh: holiday.name_kh ?? null,
    date: getDateKeyFromBackend(holiday.date),
    is_paid: holiday.is_paid,
    description: holiday.description ?? null,
  };
  Object.assign(form, normalized);
  initialFormValues.value = { ...normalized };
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  try {
    return new Intl.DateTimeFormat("en-GB", { dateStyle: "short" }).format(
      parseHolidayDate(dateString),
    );
  } catch {
    return dateString;
  }
}

/**
 * Format date/time for display
 */
function formatDatetime(value?: string | null): string {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat("en-GB", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return "-";
  }
}

function buildPayload(): PublicHolidayCreateDTO | PublicHolidayUpdateDTO {
  return {
    name: form.name.trim(),
    name_kh: form.name_kh?.trim() || null,
    date: form.date,
    is_paid: form.is_paid,
    description: form.description?.trim() || null,
  };
}

async function loadHolidays() {
  loading.value = true;
  try {
    const params: any = {};
    if (filter.value === "deleted" || filter.value === "all") {
      params.include_deleted = filter.value === "all";
      params.deleted_only = filter.value === "deleted";
    }

    holidays.value = await publicHolidayService.getPublicHolidays(params);

    if (
      (page.value - 1) * pageSize.value >= totalRows.value &&
      page.value > 1
    ) {
      page.value = Math.max(1, Math.ceil(totalRows.value / pageSize.value));
    }
  } catch (error: any) {
    console.error("Load holidays error:", error);
  } finally {
    loading.value = false;
  }
}

function openCreateDialog() {
  dialogMode.value = "create";
  currentHolidayId.value = "";
  resetForm();
  dialogVisible.value = true;
}

function openEditDialog(holiday: PublicHolidayDTO) {
  dialogMode.value = "edit";
  currentHolidayId.value = holiday.id;
  fillForm(holiday);
  dialogVisible.value = true;
}

function closeDialog() {
  dialogVisible.value = false;
  currentHolidayId.value = "";
  resetForm();
}

async function submitForm() {
  if (formError.value) {
    return;
  }

  saving.value = true;
  try {
    const payload = buildPayload();
    if (dialogMode.value === "create") {
      await publicHolidayService.createPublicHoliday(
        payload as PublicHolidayCreateDTO,
      );
      page.value = 1;
    } else {
      await publicHolidayService.updatePublicHoliday(
        currentHolidayId.value,
        payload as PublicHolidayUpdateDTO,
      );
    }

    closeDialog();
    await loadHolidays();
  } catch (error: any) {
    const errorMessage =
      error?.data?.message || error?.message || "Failed to save holiday.";
    console.error("Submit form error:", error);
  } finally {
    saving.value = false;
  }
}

async function importDefaults() {
  try {
    await ElMessageBox.confirm(
      `Import default public holidays for ${importYear.value}? Existing dates will be skipped.`,
      "Import defaults",
      {
        type: "info",
        confirmButtonText: "Import",
        cancelButtonText: "Cancel",
      },
    );

    importingDefaults.value = true;
    const result = await publicHolidayService.importDefaultPublicHolidays({
      year: importYear.value,
    });

    importSummary.value = result;
    importSummaryVisible.value = true;

    await loadHolidays();

    viewMode.value = "calendar";
    currentCalendarDate.value = new Date(importYear.value, 0, 1);
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("Import defaults error:", error);
    }
  } finally {
    importingDefaults.value = false;
  }
}

async function runByDateCheck() {
  if (!checkByDate.value) return;

  checkingByDate.value = true;
  byDateChecked.value = false;
  byDateResult.value = null;

  try {
    byDateResult.value = await publicHolidayService.getPublicHolidayByDate(
      checkByDate.value,
    );
    byDateChecked.value = true;
  } catch (error: any) {
    console.error("By-date check error:", error);
  } finally {
    checkingByDate.value = false;
  }
}

async function confirmDelete(holiday: PublicHolidayDTO) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete "${holiday.name}"? This action can be undone.`,
      "Delete holiday",
      {
        type: "warning",
        confirmButtonText: "Delete",
        cancelButtonText: "Cancel",
      },
    );

    actionLoading.value[holiday.id] = true;
    await publicHolidayService.softDeletePublicHoliday(holiday.id);

    await loadHolidays();
  } catch (error: any) {
    if (error !== "cancel") {
      const errorMessage =
        error?.data?.message || error?.message || "Failed to delete holiday.";
      console.error("Delete error:", error);
    }
  } finally {
    actionLoading.value[holiday.id] = false;
  }
}

async function confirmRestore(holiday: PublicHolidayDTO) {
  try {
    await ElMessageBox.confirm(
      `Restore "${holiday.name}"?`,
      "Restore holiday",
      {
        type: "info",
        confirmButtonText: "Restore",
        cancelButtonText: "Cancel",
      },
    );

    actionLoading.value[holiday.id] = true;
    await publicHolidayService.restorePublicHoliday(holiday.id);

    await loadHolidays();
  } catch (error: any) {
    if (error !== "cancel") {
      const errorMessage =
        error?.data?.message || error?.message || "Failed to restore holiday.";
      console.error("Restore error:", error);
    }
  } finally {
    actionLoading.value[holiday.id] = false;
  }
}

function onFilterChange() {
  // Reset to first page when filter changes
  page.value = 1;
}

// Calendar functions
function previousMonth() {
  currentCalendarDate.value = new Date(
    currentCalendarDate.value.getFullYear(),
    currentCalendarDate.value.getMonth() - 1,
    1,
  );
}

function nextMonth() {
  currentCalendarDate.value = new Date(
    currentCalendarDate.value.getFullYear(),
    currentCalendarDate.value.getMonth() + 1,
    1,
  );
}

function openCalendarSummary(
  dateHolidays: PublicHolidayDTO[],
  dateStr: string,
) {
  selectedCalendarDateHolidays.value = dateHolidays;
  currentCalendarDate.value = parseHolidayDate(dateStr);
  calendarSummaryVisible.value = true;
}

function closeCalendarSummary() {
  calendarSummaryVisible.value = false;
  selectedCalendarDateHolidays.value = [];
}

// Lifecycle hooks
onMounted(async () => {
  await loadHolidays();
});

// Watch for filter changes to reload data
watch(filter, async () => {
  onFilterChange();
  await loadHolidays();
});
</script>

<template>
  <div class="holiday-page">
    <OverviewHeader
      :title="'Public Holidays'"
      :description="'Create and manage public holidays for the HRMS system.'"
      :backPath="'/hr/config'"
    >
      <template #actions>
        <div class="holiday-header-actions">
          <div class="header-import-tools">
            <el-input-number
              v-model="importYear"
              :min="2000"
              :max="2100"
              :step="1"
              controls-position="right"
              size="default"
            />
            <BaseButton
              type="success"
              :loading="importingDefaults"
              :disabled="loading || importingDefaults"
              @click="importDefaults"
            >
              <template #iconPre>
                <el-icon><Upload /></el-icon>
              </template>
              Import Defaults
            </BaseButton>
          </div>

          <BaseButton
            plain
            :loading="loading"
            class="holiday-header-btn holiday-header-btn--refresh"
            @click="loadHolidays"
          >
            <template #iconPre>
              <el-icon><Refresh /></el-icon>
            </template>
            Refresh
          </BaseButton>

          <BaseButton
            type="primary"
            class="holiday-header-btn"
            :disabled="loading"
            @click="openCreateDialog"
          >
            <template #iconPre>
              <el-icon><Plus /></el-icon>
            </template>
            Add Holiday
          </BaseButton>
        </div>
      </template>
    </OverviewHeader>

    <div class="holiday-view-toggle">
      <el-segmented
        v-model="viewMode"
        :options="[
          { label: 'Table View', value: 'table' },
          { label: 'Calendar View', value: 'calendar' },
        ]"
      />
    </div>

    <div v-if="viewMode === 'table'" class="holiday-table-view">
      <div class="holiday-summary-grid">
        <div
          v-for="item in summaryCards"
          :key="item.label"
          class="holiday-summary-card"
        >
          <div class="holiday-summary-label">{{ item.label }}</div>
          <div class="holiday-summary-value">{{ item.value }}</div>
        </div>
      </div>

      <div class="holiday-toolbar">
        <el-input
          v-model="q"
          clearable
          placeholder="Search holidays by name, date, or description"
          @input="onFilterChange"
          @clear="onFilterChange"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select
          v-model="selectedYear"
          clearable
          placeholder="Filter by year"
          @change="onFilterChange"
        >
          <el-option
            v-for="year in availableYears"
            :key="year"
            :label="`${year}`"
            :value="year"
          />
        </el-select>

        <el-segmented
          v-model="filter"
          :options="[
            { label: 'Active', value: 'active' },
            { label: 'Deleted', value: 'deleted' },
            { label: 'All', value: 'all' },
          ]"
          @change="onFilterChange"
        />
      </div>

      <div class="holiday-by-date-checker">
        <div class="holiday-by-date-header">
          <el-icon><Calendar /></el-icon>
          <span>Check Holiday By Date</span>
        </div>

        <div class="holiday-by-date-controls">
          <el-date-picker
            v-model="checkByDate"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            placeholder="Select date"
            style="width: 100%"
          />
          <BaseButton
            type="primary"
            :loading="checkingByDate"
            @click="runByDateCheck"
          >
            Check Date
          </BaseButton>
        </div>

        <div v-if="byDateChecked" class="holiday-by-date-result">
          <el-alert
            v-if="byDateResult"
            title="Holiday found for selected date"
            type="success"
            :closable="false"
            show-icon
          />
          <el-alert
            v-else
            title="No holiday found for selected date"
            type="info"
            :closable="false"
            show-icon
          />
        </div>
      </div>

      <div class="holiday-table-card">
        <SmartTable
          :columns="tableColumns"
          :data="pagedHolidays"
          :loading="loading"
          :total="totalRows"
          :page="page"
          :page-size="pageSize"
          @page="page = $event"
          @page-size="pageSize = $event"
        >
          <template #name_kh="{ row }">
            <span>{{ (row as PublicHolidayDTO).name_kh || "-" }}</span>
          </template>

          <template #date="{ row }">
            <span class="holiday-date">
              {{ formatDate((row as PublicHolidayDTO).date) }}
            </span>
          </template>

          <template #paid_status="{ row }">
            <el-tag
              :type="(row as PublicHolidayDTO).is_paid ? 'success' : 'info'"
              effect="light"
            >
              {{ (row as PublicHolidayDTO).is_paid ? "Paid" : "Unpaid" }}
            </el-tag>
          </template>

          <template #description="{ row }">
            <span class="holiday-description">
              {{ (row as PublicHolidayDTO).description || "-" }}
            </span>
          </template>

          <template #updated_at="{ row }">
            <div class="holiday-datetime">
              <div>
                {{
                  formatDatetime(
                    (row as PublicHolidayDTO).lifecycle?.updated_at,
                  )
                }}
              </div>
              <div class="text-xs text-gray-500">
                by
                {{
                  displayRelation(
                    (row as PublicHolidayDTO).created_by_name,
                    (row as PublicHolidayDTO).created_by,
                  )
                }}
              </div>
            </div>
          </template>

          <template #operation="{ row }">
            <div class="holiday-actions">
              <BaseButton
                v-if="!(row as PublicHolidayDTO).lifecycle?.deleted_at"
                type="primary"
                link
                size="small"
                @click="openEditDialog(row as PublicHolidayDTO)"
              >
                <template #iconPre>
                  <el-icon><Edit /></el-icon>
                </template>
                Edit
              </BaseButton>

              <BaseButton
                v-if="!(row as PublicHolidayDTO).lifecycle?.deleted_at"
                type="danger"
                link
                size="small"
                :loading="actionLoading[(row as PublicHolidayDTO).id]"
                @click="confirmDelete(row as PublicHolidayDTO)"
              >
                <template #iconPre>
                  <el-icon><Delete /></el-icon>
                </template>
                Delete
              </BaseButton>

              <BaseButton
                v-else
                type="success"
                link
                size="small"
                :loading="actionLoading[(row as PublicHolidayDTO).id]"
                @click="confirmRestore(row as PublicHolidayDTO)"
              >
                <template #iconPre>
                  <el-icon><RefreshLeft /></el-icon>
                </template>
                Restore
              </BaseButton>
            </div>
          </template>
        </SmartTable>
      </div>
    </div>

    <!-- Calendar View -->
    <div v-if="viewMode === 'calendar'" class="holiday-calendar-view">
      <div class="calendar-header">
        <BaseButton @click="previousMonth">
          <template #iconPre>
            <el-icon><ArrowLeftBold /></el-icon>
          </template>
          Previous
        </BaseButton>
        <h2 class="calendar-month-year">{{ monthYear }}</h2>
        <BaseButton @click="nextMonth">
          Next
          <template #iconPost>
            <el-icon><ArrowRightBold /></el-icon>
          </template>
        </BaseButton>
      </div>

      <div class="calendar-container">
        <div class="calendar-weekdays">
          <div
            v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']"
            :key="day"
            class="calendar-weekday"
          >
            {{ day }}
          </div>
        </div>

        <div class="calendar-grid">
          <div
            v-for="day in calendarDays"
            :key="day.dateStr"
            :class="[
              'calendar-day',
              {
                'calendar-day--other-month': !day.isCurrentMonth,
                'calendar-day--holiday': day.hasHoliday,
                'calendar-day--today': day.isToday,
              },
            ]"
            @click="
              day.hasHoliday && openCalendarSummary(day.holidays, day.dateStr)
            "
          >
            <div class="calendar-day-topline">
              <div class="calendar-day-number">{{ day.date.getDate() }}</div>
              <div v-if="day.holidayCount" class="calendar-day-count">
                {{ day.holidayCount }}
              </div>
            </div>

            <div v-if="day.hasHoliday" class="calendar-day-holidays">
              <div
                v-for="holiday in day.holidays.slice(0, 2)"
                :key="holiday.id"
                class="calendar-holiday-pill"
              >
                {{ holiday.name }}
              </div>
              <div v-if="day.holidays.length > 2" class="calendar-more-pill">
                +{{ day.holidays.length - 2 }} more
              </div>
            </div>

            <div v-if="day.hasHoliday" class="calendar-holiday-indicator">
              <div class="holiday-dot" />
            </div>
          </div>
        </div>
      </div>

      <div class="calendar-legend">
        <div class="legend-item">
          <div class="legend-dot" />
          <span>Holidays</span>
        </div>
        <div class="legend-item">
          <div class="legend-today" />
          <span>Today</span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="`${dialogMode === 'create' ? 'Add' : 'Edit'} Holiday`"
      width="500px"
      @close="closeDialog"
    >
      <div class="holiday-form-content">
        <div class="holiday-form-group">
          <label class="holiday-form-label">Holiday Name *</label>
          <el-input
            v-model="form.name"
            placeholder="e.g., Independence Day"
            clearable
            maxlength="100"
            show-word-limit
          />
        </div>

        <div class="holiday-form-group">
          <label class="holiday-form-label">ឈ្មោះក្នុងខ្មែរ</label>
          <el-input
            v-model="form.name_kh"
            placeholder="e.g., ថ្ងៃឯករាជ្យ"
            clearable
            maxlength="100"
            show-word-limit
          />
        </div>

        <div class="holiday-form-group">
          <label class="holiday-form-label">Date *</label>
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="Pick a date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </div>

        <div class="holiday-form-group">
          <el-checkbox v-model="form.is_paid"> Paid Holiday </el-checkbox>
        </div>

        <div class="holiday-form-group">
          <label class="holiday-form-label">Description</label>
          <el-input
            v-model="form.description"
            type="textarea"
            placeholder="Add notes or description"
            maxlength="500"
            show-word-limit
            rows="4"
          />
        </div>

        <div v-if="formError" class="holiday-form-error">
          {{ formError }}
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <BaseButton @click="closeDialog">Cancel</BaseButton>
          <BaseButton
            type="primary"
            :loading="saving"
            :disabled="!canSubmitForm"
            @click="submitForm"
          >
            {{ dialogMode === "create" ? "Create" : "Update" }}
          </BaseButton>
        </span>
      </template>
    </el-dialog>

    <!-- Calendar Summary Popup -->
    <el-dialog
      v-model="calendarSummaryVisible"
      :title="calendarSummaryTitle"
      width="600px"
      @close="closeCalendarSummary"
    >
      <div class="calendar-summary-content">
        <div
          v-for="holiday in selectedCalendarDateHolidays"
          :key="holiday.id"
          class="summary-holiday-card"
        >
          <div class="summary-holiday-header">
            <div class="summary-holiday-name">{{ holiday.name }}</div>
            <el-tag
              :type="holiday.is_paid ? 'success' : 'info'"
              effect="light"
              size="small"
            >
              {{ holiday.is_paid ? "Paid" : "Unpaid" }}
            </el-tag>
          </div>

          <div v-if="holiday.name_kh" class="summary-holiday-kh">
            {{ holiday.name_kh }}
          </div>

          <div v-if="holiday.description" class="summary-holiday-description">
            {{ holiday.description }}
          </div>

          <div class="summary-holiday-info">
            <div class="info-item">
              <span class="info-label">Date:</span>
              <span class="info-value">{{ formatDate(holiday.date) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Created:</span>
              <span class="info-value">{{
                formatDatetime(holiday.lifecycle?.created_at)
              }}</span>
            </div>
          </div>

          <div class="summary-holiday-actions">
            <BaseButton
              type="primary"
              link
              size="small"
              @click="
                openEditDialog(holiday);
                closeCalendarSummary();
              "
            >
              <template #iconPre>
                <el-icon><Edit /></el-icon>
              </template>
              Edit
            </BaseButton>
            <BaseButton
              type="danger"
              link
              size="small"
              @click="
                confirmDelete(holiday);
                closeCalendarSummary();
              "
            >
              <template #iconPre>
                <el-icon><Delete /></el-icon>
              </template>
              Delete
            </BaseButton>
          </div>
        </div>
      </div>
    </el-dialog>

    <el-dialog
      v-model="importSummaryVisible"
      title="Import Summary"
      width="640px"
    >
      <div v-if="importSummary" class="import-summary-content">
        <div class="import-summary-grid">
          <div class="import-summary-card">
            <div class="import-summary-label">Year</div>
            <div class="import-summary-value">{{ importSummary.year }}</div>
          </div>
          <div class="import-summary-card success">
            <div class="import-summary-label">Imported</div>
            <div class="import-summary-value">
              {{ importSummary.imported_count }}
            </div>
          </div>
          <div class="import-summary-card warning">
            <div class="import-summary-label">Skipped</div>
            <div class="import-summary-value">
              {{ importSummary.skipped_count }}
            </div>
          </div>
        </div>

        <div v-if="importSummary.imported.length" class="import-list-block">
          <div class="import-list-title">Imported Holidays</div>
          <div class="import-list">
            <div
              v-for="holiday in importSummary.imported"
              :key="holiday.id"
              class="import-list-item"
            >
              <span class="name">{{ holiday.name }}</span>
              <span class="date">{{ formatDate(holiday.date) }}</span>
            </div>
          </div>
        </div>

        <div
          v-if="importSummary.skipped_dates.length"
          class="import-list-block skipped"
        >
          <div class="import-list-title">Skipped Dates (already existed)</div>
          <div class="import-list dates">
            <span
              v-for="date in importSummary.skipped_dates"
              :key="date"
              class="skip-date-chip"
            >
              {{ date }}
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <BaseButton type="primary" @click="importSummaryVisible = false">
            Close
          </BaseButton>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.holiday-page {
  padding: 24px;
  background: var(--color-bg);
  min-height: 100vh;
}

.header-import-tools {
  display: flex;
  align-items: center;
  gap: 10px;

  :deep(.el-input-number) {
    width: 140px;
  }
}

.holiday-header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.holiday-header-actions :deep(.el-button) {
  min-height: 36px;
  border-radius: 10px;
  font-weight: 650;
}

.holiday-header-btn--refresh {
  border-color: color-mix(
    in srgb,
    var(--border-color) 60%,
    var(--color-primary) 40%
  ) !important;
  color: color-mix(
    in srgb,
    var(--text-color) 82%,
    var(--color-primary) 18%
  ) !important;
  background: color-mix(
    in srgb,
    var(--color-card) 94%,
    var(--color-bg) 6%
  ) !important;
}

.holiday-header-btn--refresh:hover:not(.is-disabled):not([disabled]) {
  background: var(--hover-bg) !important;
  border-color: color-mix(
    in srgb,
    var(--border-color) 48%,
    var(--color-primary) 52%
  ) !important;
}

.holiday-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.holiday-summary-card {
  padding: 16px;
  background: var(--color-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  box-shadow: 0 1px 3px var(--card-shadow);
}

.holiday-summary-label {
  font-size: 12px;
  color: var(--muted-color);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.holiday-summary-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-primary);
}

.holiday-toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;

  :deep(.el-input) {
    flex: 1;
    min-width: 200px;
  }

  :deep(.el-select) {
    min-width: 150px;
  }

  :deep(.el-segmented) {
    min-width: 250px;
  }

  @media (max-width: 600px) {
    flex-direction: column;

    :deep(.el-input),
    :deep(.el-select),
    :deep(.el-segmented) {
      width: 100%;
    }
  }
}

.holiday-table-card {
  background: var(--color-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 16px;
  box-shadow: 0 1px 3px var(--card-shadow);
}

.holiday-by-date-checker {
  border: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.holiday-by-date-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
}

.holiday-by-date-controls {
  display: grid;
  grid-template-columns: 1fr 130px;
  gap: 10px;
}

.holiday-by-date-result {
  margin-top: 10px;
}

.holiday-date {
  font-weight: 500;
  color: var(--color-primary);
}

.holiday-description {
  color: var(--muted-color);
  display: block;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.holiday-datetime {
  font-size: 12px;
  line-height: 1.6;

  div:first-child {
    color: var(--text-color);
    font-weight: 500;
  }
}

.holiday-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.holiday-form-content {
  padding: 16px 0;
}

.holiday-form-group {
  margin-bottom: 16px;

  &:last-of-type {
    margin-bottom: 0;
  }
}

.holiday-form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
}

.holiday-form-error {
  margin-top: 16px;
  padding: 12px;
  background: color-mix(
    in srgb,
    var(--el-color-warning) 10%,
    var(--color-card)
  );
  border-left: 3px solid var(--el-color-warning);
  color: var(--el-color-warning);
  font-size: 12px;
  border-radius: 2px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

// View toggle
.holiday-view-toggle {
  margin-bottom: 24px;
  display: flex;
  gap: 12px;

  :deep(.el-segmented) {
    background: var(--color-card);
    border: 1px solid var(--border-color);
    border-radius: 4px;
  }
}

// Table view
.holiday-table-view {
  animation: fadeIn 0.3s ease-in-out;
}

// Calendar view
.holiday-calendar-view {
  animation: fadeIn 0.3s ease-in-out;
  background: radial-gradient(
      circle at top right,
      color-mix(in srgb, var(--color-primary) 8%, var(--color-card) 92%) 0%,
      transparent 40%
    ),
    var(--color-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 10px 30px var(--card-shadow);
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;

  :deep(.el-button) {
    min-width: 120px;
  }
}

.calendar-month-year {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color);
  flex: 1;
  text-align: center;
  margin: 0;
}

.calendar-container {
  margin-bottom: 24px;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.calendar-weekday {
  padding: 10px;
  text-align: center;
  font-weight: 600;
  color: var(--muted-color);
  font-size: 11px;
  text-transform: uppercase;
  border-bottom: 1px solid var(--border-color);
  letter-spacing: 0.08em;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.calendar-day {
  min-height: 110px;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: flex-start;
  gap: 6px;
  background: var(--color-card);
  transition: all 0.2s ease;
  cursor: default;

  &--other-month {
    opacity: 0.3;
    background: color-mix(in srgb, var(--color-card) 94%, var(--color-bg) 6%);
  }

  &--holiday {
    cursor: pointer;
    background: color-mix(
      in srgb,
      var(--color-primary) 8%,
      var(--color-card) 92%
    );
    border-color: var(--color-primary);
    font-weight: 500;

    &:hover {
      background: color-mix(
        in srgb,
        var(--color-primary) 15%,
        var(--color-card) 85%
      );
      box-shadow: 0 2px 8px var(--card-shadow);
      transform: translateY(-2px);
    }
  }

  &--today {
    box-shadow: inset 0 0 0 2px
      color-mix(in srgb, var(--color-primary) 45%, var(--color-card));
  }
}

.calendar-day-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.calendar-day-number {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-color);
}

.calendar-day-count {
  min-width: 20px;
  height: 20px;
  border-radius: 999px;
  background: var(--color-primary);
  color: var(--color-light);
  font-size: 11px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  font-weight: 600;
}

.calendar-day-holidays {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.calendar-holiday-pill,
.calendar-more-pill {
  font-size: 10px;
  line-height: 1.2;
  padding: 3px 6px;
  border-radius: 999px;
  width: fit-content;
  max-width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.calendar-holiday-pill {
  background: color-mix(in srgb, var(--color-primary) 14%, var(--color-card));
  color: var(--color-primary);
}

.calendar-more-pill {
  background: color-mix(in srgb, var(--color-card) 88%, var(--color-bg) 12%);
  color: var(--muted-color);
}

.calendar-holiday-indicator {
  display: none;
  gap: 2px;
  align-items: center;
  justify-content: center;
}

.holiday-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary);
}

.calendar-legend {
  display: flex;
  gap: 24px;
  padding: 16px;
  background: color-mix(in srgb, var(--color-card) 94%, var(--color-bg) 6%);
  border-radius: 4px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--muted-color);
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
}

.legend-today {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  border: 2px solid var(--color-primary);
}

// Calendar summary popup
.calendar-summary-content {
  padding: 16px 0;
}

.summary-holiday-card {
  padding: 16px;
  background: color-mix(in srgb, var(--color-card) 94%, var(--color-bg) 6%);
  border-left: 3px solid var(--color-primary);
  border-radius: 2px;
  margin-bottom: 16px;

  &:last-child {
    margin-bottom: 0;
  }
}

.summary-holiday-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.summary-holiday-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
  flex: 1;
}

.summary-holiday-kh {
  font-size: 14px;
  color: var(--muted-color);
  margin-bottom: 8px;
  font-weight: 500;
}

.summary-holiday-description {
  font-size: 13px;
  color: var(--muted-color);
  line-height: 1.5;
  margin-bottom: 12px;
  padding: 8px 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.summary-holiday-info {
  font-size: 12px;
  color: var(--muted-color);
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;

  &:last-child {
    margin-bottom: 0;
  }
}

.info-label {
  font-weight: 600;
  color: var(--muted-color);
  min-width: 60px;
}

.info-value {
  color: var(--text-color);
}

.summary-holiday-actions {
  display: flex;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.import-summary-content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.import-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.import-summary-card {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 14px;
  background: color-mix(in srgb, var(--color-card) 96%, var(--color-bg) 4%);
}

.import-summary-card.success {
  background: color-mix(
    in srgb,
    var(--button-success-bg) 8%,
    var(--color-card) 92%
  );
  border-color: color-mix(
    in srgb,
    var(--button-success-bg) 25%,
    var(--border-color) 75%
  );
}

.import-summary-card.warning {
  background: color-mix(
    in srgb,
    var(--button-warning-bg) 10%,
    var(--color-card) 90%
  );
  border-color: color-mix(
    in srgb,
    var(--button-warning-bg) 25%,
    var(--border-color) 75%
  );
}

.import-summary-label {
  font-size: 12px;
  color: var(--muted-color);
}

.import-summary-value {
  margin-top: 6px;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-color);
}

.import-list-block {
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 12px;
}

.import-list-block.skipped {
  background: color-mix(in srgb, var(--color-card) 96%, var(--color-bg) 4%);
}

.import-list-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 10px;
}

.import-list {
  max-height: 180px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.import-list.dates {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8px;
}

.import-list-item {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
}

.import-list-item .name {
  color: var(--text-color);
  font-weight: 500;
}

.import-list-item .date {
  color: var(--muted-color);
}

.skip-date-chip {
  padding: 4px 8px;
  background: color-mix(in srgb, var(--color-card) 88%, var(--color-bg) 12%);
  border-radius: 999px;
  font-size: 12px;
  color: var(--muted-color);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .holiday-page {
    padding: 16px;
  }

  .holiday-header-actions {
    width: 100%;
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;

    :deep(.el-button) {
      width: 100%;
    }
  }

  .header-import-tools {
    width: 100%;
    margin-right: 0;
    display: grid;
    grid-template-columns: 1fr;

    :deep(.el-input-number) {
      width: 100%;
    }

    :deep(.el-button) {
      width: 100%;
    }
  }

  .calendar-header {
    flex-direction: column;
    gap: 12px;
  }

  .calendar-month-year {
    font-size: 18px;
  }

  .calendar-day {
    min-height: 88px;
    padding: 4px;
  }

  .calendar-day-number {
    font-size: 12px;
  }

  .holiday-dot {
    width: 4px;
    height: 4px;
  }

  .calendar-legend {
    flex-direction: column;
    gap: 8px;
  }

  .import-summary-grid {
    grid-template-columns: 1fr;
  }

  .holiday-by-date-controls {
    grid-template-columns: 1fr;
  }
}
</style>
