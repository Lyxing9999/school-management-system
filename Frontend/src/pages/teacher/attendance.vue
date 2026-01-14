<script setup lang="ts">
definePageMeta({ layout: "default" });

import { ref, computed, watch } from "vue";
import { storeToRefs } from "pinia";
import {
  ElMessage,
  ElMessageBox,
  ElSelect,
  ElOption,
  ElInput,
  ElDatePicker,
  ElTag,
  ElForm,
  ElRow,
  ElCol,
  ElAlert,
  ElCard,
  ElEmpty,
  ElSkeleton,
  ElPagination,
} from "element-plus";

import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
dayjs.extend(utc);
dayjs.extend(timezone);

import { teacherService } from "~/api/teacher";
import type { AttendanceDTO, AttendanceStatus } from "~/api/types/school.dto";
import type { Field } from "~/components/types/form";
import type { ColumnConfig } from "~/components/types/tableEdit";

import TeacherClassSelect from "~/components/selects/class/TeacherClassSelect.vue";
import TeacherStudentSelect from "~/components/selects/subject/TeacherClassStudentSelect.vue";
import TeacherSubjectSelect from "~/components/selects/subject/TeacherSubjectSelect.vue";
import TeacherScheduleSlotSelect from "~/components/selects/schedule/TeacherScheduleSlotSelect.vue";

import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import SmartFormDialog from "~/components/form/SmartFormDialog.vue";

import ActionButtons from "~/components/buttons/ActionButtons.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";

import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { useHeaderState } from "~/composables/ui/useHeaderState";

import { usePreferencesStore } from "~/stores/preferencesStore";
import { formatDate } from "~/utils/date/formatDate";
import { reportError } from "~/utils/errors/errors";

const api = teacherService();
const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);

const KH_TZ = "Asia/Phnom_Penh";
const todayISO = dayjs().tz(KH_TZ).format("YYYY-MM-DD");

/* ---------------- types ---------------- */
type AttendanceEnriched = AttendanceDTO & {
  student_name?: string;
  class_name?: string;
  teacher_name?: string;
  subject_label?: string;
  subject_id?: string;
  schedule_slot_id?: string;
};

type AttendanceFormModel = {
  student_id: string;
  status: AttendanceStatus | "";
  record_date: string;
  subject_id: string;
  schedule_slot_id: string;
};

type EditAttendanceFormModel = {
  student_name: string;
  attendance_id: string;
  status: AttendanceStatus | "";
};

type ScheduleSlotSelectItem = {
  value: string;
  label: string;
  class_id?: string;
  day_of_week?: number;
  start_time?: string;
  end_time?: string;
  room?: string;
  subject_id?: string;
  subject_label?: string;
};

/* ---------------- filters ---------------- */
const selectedClassId = ref<string | null>(null);
const selectedDate = ref<string>(todayISO);
const selectedSlotFilterId = ref<string | null>(null);

/* ---------------- schedule slot cache ---------------- */
const scheduleSlotOptions = ref<ScheduleSlotSelectItem[]>([]);

const scheduleSlotMap = computed(() => {
  const m = new Map<string, ScheduleSlotSelectItem>();
  for (const it of scheduleSlotOptions.value) {
    const id = String(it?.value ?? "");
    if (id) m.set(id, it);
  }
  return m;
});

const hasNoSlotsForTeacher = ref(false);

async function loadScheduleSlotOptions() {
  hasNoSlotsForTeacher.value = false;

  if (!selectedClassId.value) {
    scheduleSlotOptions.value = [];
    return;
  }

  try {
    const res = await api.teacher.listScheduleSlotSelect(
      {
        class_id: selectedClassId.value,
        date: selectedDate.value,
      },
      { showError: false } as any
    );

    const payload = (res as any)?.data ?? res;
    const items = (payload?.items ?? []) as ScheduleSlotSelectItem[];

    scheduleSlotOptions.value = items;

    if (items.length === 0) {
      hasNoSlotsForTeacher.value = true;
      ElMessage.warning(
        "You have no teaching schedule for this class on this date."
      );
    }
  } catch (err) {
    scheduleSlotOptions.value = [];
    console.error(err);
  }
}

/* ---------------- View Helpers ---------------- */
function getSlotDisplay(slotId: string) {
  if (!slotId) return null;
  const slot = scheduleSlotMap.value.get(String(slotId));
  if (!slot) return null;

  return {
    timeRange: formatTimeRange(slot.start_time, slot.end_time),
    label: slot.label,
    room: slot.room,
  };
}

function getStatusTagType(status: string) {
  if (status === "present") return "success";
  if (status === "excused") return "warning";
  return "danger";
}

function formatTimeRange(start?: string, end?: string) {
  const s = String(start ?? "");
  const e = String(end ?? "");
  if (!s || !e) return "";
  return `${s}–${e}`;
}

/* ---------------- per-row loading ---------------- */
const detailLoadingId = ref<string | null>(null);
const deleteLoadingId = ref<string | null>(null);

const isDetailLoading = (id: string) => detailLoadingId.value === id;
const isDeleteLoading = (id: string) => deleteLoadingId.value === id;

/* ---------------- paginated fetch ---------------- */
const {
  data: attendanceList,
  error: tableError,
  currentPage,
  pageSize,
  totalRows,
  initialLoading,
  fetching,
  fetchPage,
  goPage,
} = usePaginatedFetch<
  AttendanceEnriched,
  { classId: string | null; date: string; slotId: string }
>(
  async (filter, page, size, signal) => {
    const classId = filter?.classId;
    const date = filter?.date;
    const slotId = filter?.slotId;

    if (!classId) return { items: [], total: 0 };

    const res = await api.teacher.listAttendanceForClass(classId, { date }, {
      signal,
      showError: false,
    } as any);

    const payload = (res as any)?.data ?? res;
    const all = (payload?.items ?? []) as AttendanceEnriched[];

    const filtered = slotId
      ? all.filter((x: any) => String(x?.schedule_slot_id ?? "") === slotId)
      : all;

    const sorted = filtered.slice().sort((a: any, b: any) => {
      const ad = new Date(a?.record_date ?? a?.date ?? 0).getTime();
      const bd = new Date(b?.record_date ?? b?.date ?? 0).getTime();
      return bd - ad;
    });

    const total = Number((payload as any)?.total ?? sorted.length);
    const start = (page - 1) * size;
    const end = start + size;

    return {
      items: sorted.slice(start, end),
      total: slotId ? sorted.length : total,
    };
  },
  {
    initialPage: 1,
    pageSizeRef: tablePageSize,
    filter: computed(() => ({
      classId: selectedClassId.value,
      date: selectedDate.value,
      slotId: selectedSlotFilterId.value || "",
    })),
  }
);

const tableLoading = computed(() => initialLoading.value || fetching.value);
const errorMessage = computed(() => tableError.value?.message ?? null);

function clearError() {
  /* no-op */
}

/* ---------------- forms ---------------- */
const attendanceForm = ref<AttendanceFormModel>({
  student_id: "",
  status: "" as AttendanceStatus | "",
  record_date: selectedDate.value || todayISO,
  subject_id: "",
  schedule_slot_id: "",
});

const editAttendanceForm = ref<EditAttendanceFormModel>({
  attendance_id: "",
  status: "" as AttendanceStatus | "",
  student_name: "",
});

const addDialogVisible = ref(false);
const addDialogLoading = ref(false);
const editDialogVisible = ref(false);
const editDialogLoading = ref(false);
const originalEditStatus = ref<AttendanceStatus | "">("");
const selectedAddSlot = ref<any | null>(null);

/* ---------------- computed ---------------- */
const hasClassSelected = computed(() => !!selectedClassId.value);
const isFirstLoad = computed(
  () => tableLoading.value && attendanceList.value.length === 0
);

const showingText = computed(() => {
  const total = Number(totalRows.value || 0);
  if (!total) return "No records";
  const start = (currentPage.value - 1) * pageSize.value + 1;
  const end = Math.min(currentPage.value * pageSize.value, total);
  return `Showing ${start}-${end} of ${total}`;
});

const statusSummary = computed(() => {
  const summary = {
    total: attendanceList.value.length,
    present: 0,
    absent: 0,
    excused: 0,
  };
  for (const rec of attendanceList.value) {
    if (rec.status === "present") summary.present++;
    else if (rec.status === "absent") summary.absent++;
    else if (rec.status === "excused") summary.excused++;
  }
  return summary;
});

const presentRate = computed(() => {
  if (!statusSummary.value.total) return null;
  return (
    Math.round(
      (statusSummary.value.present / statusSummary.value.total) * 1000
    ) / 10
  );
});

/* ---------------- watchers ---------------- */
/**
 * Senior-grade tweak:
 * - when class/date changes, reset slot filter immediately (prevents stale slotId)
 * - reload slot options
 * - then fetch page 1
 */
watch(
  () => [selectedClassId.value, selectedDate.value],
  async () => {
    attendanceForm.value.record_date = selectedDate.value || todayISO;
    attendanceForm.value.student_id = "";

    // reset slot filter (clean UX)
    selectedSlotFilterId.value = null;

    goPage(1);

    await loadScheduleSlotOptions();
    await fetchPage(1);
  },
  { immediate: true }
);

/* ---------------- SmartForm Fields ---------------- */
const addAttendanceFields = computed(() => {
  const slot = selectedAddSlot.value;
  const slotHasSubject = !!slot?.subject_id;

  const fields: Field<AttendanceFormModel>[] = [
    {
      key: "schedule_slot_id",
      label: "Schedule slot",
      component: TeacherScheduleSlotSelect,
      formItemProps: { required: true },
      componentProps: {
        classId: selectedClassId.value || "",
        date: selectedDate.value,
        placeholder: "Select schedule slot",
        disabled: !selectedClassId.value,
        multiple: false,
        limit: 200,

        // Make sure it fills the row
        style: "width: 100%",
        class: "w-full",

        // UX: keep selected slot in state + auto-set subject_id
        onSelected: (s: any) => {
          selectedAddSlot.value = s ?? null;
          attendanceForm.value.subject_id = String(s?.subject_id || "");
        },
      },
    },

    ...(slotHasSubject
      ? ([
          {
            key: "subject_id",
            label: "Subject",
            component: ElInput,
            componentProps: {
              modelValue: String(slot?.subject_label ?? ""),
              disabled: true,
              placeholder: "Auto-filled from slot",
            },
          },
        ] as Field<AttendanceFormModel>[])
      : ([
          {
            key: "subject_id",
            label: "Subject",
            component: TeacherSubjectSelect,
            componentProps: {
              classId: selectedClassId.value || "",
              placeholder: "Select subject",
              disabled: !selectedClassId.value,
              style: "width: 100%",
            },
          },
        ] as Field<AttendanceFormModel>[])),

    {
      key: "student_id",
      label: "Student",
      component: TeacherStudentSelect,
      formItemProps: { required: true },
      componentProps: {
        classId: selectedClassId.value || "",
        reload: true,
        multiple: false,
        placeholder: "Select student",
        disabled: !selectedClassId.value,
        style: "width: 100%",
      },
    },

    {
      key: "status",
      label: "Status",
      component: ElSelect,
      childComponent: ElOption,
      formItemProps: { required: true },
      childComponentProps: {
        options: [
          { label: "Present", value: "present" },
          { label: "Absent", value: "absent" },
          { label: "Excused", value: "excused" },
        ],
        labelKey: "label",
        valueKey: "value",
      },
      componentProps: { placeholder: "Select status", style: "width: 100%" },
    },

    {
      key: "record_date",
      label: "Date",
      component: ElDatePicker,
      formItemProps: { required: true },
      componentProps: {
        type: "date",
        format: "YYYY-MM-DD",
        valueFormat: "YYYY-MM-DD",
        placeholder: "Pick a day",
        style: "width: 100%",
        disabled: true,
      },
    },
  ];

  return fields;
});

const editAttendanceFields: Field<EditAttendanceFormModel>[] = [
  {
    key: "student_name",
    label: "Student",
    component: ElInput,
    componentProps: { disabled: true, placeholder: "Student name" },
  },
  {
    key: "status",
    label: "Status",
    component: ElSelect,
    childComponent: ElOption,
    childComponentProps: {
      options: [
        { label: "Present", value: "present" },
        { label: "Absent", value: "absent" },
        { label: "Excused", value: "excused" },
      ],
      labelKey: "label",
      valueKey: "value",
    },
    componentProps: { placeholder: "Select status", style: "width: 100%" },
  },
];

/* ---------------- Actions ---------------- */
async function loadAttendance(page = currentPage.value || 1) {
  await fetchPage(page);
}

async function handleRefresh() {
  await loadScheduleSlotOptions();
  await loadAttendance(1);
}

function extractPydanticValidationMessage(err: any): string | null {
  const payload = err?.response?.data ?? err?.data ?? err;
  if (!payload || typeof payload !== "object") return null;

  const code = payload?.code;
  const userMessage = payload?.user_message || payload?.message;

  if (
    code === "PYDANTICBASEVALIDATIONERROR_ERROR" ||
    payload?.error === "PYDANTICBASEVALIDATIONERROR_ERROR"
  ) {
    return userMessage || "Validation failed.";
  }
  return null;
}

async function submitAttendance(): Promise<boolean> {
  const form = attendanceForm.value;

  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return false;
  }

  if (!form.subject_id && selectedAddSlot.value?.subject_id) {
    form.subject_id = String(selectedAddSlot.value.subject_id);
  }

  if (
    !form.schedule_slot_id ||
    !form.student_id ||
    !form.status ||
    !form.subject_id
  ) {
    ElMessage.warning("Please complete the form.");
    return false;
  }

  try {
    const dto = await api.teacher.markAttendance(
      {
        student_id: form.student_id,
        class_id: selectedClassId.value,
        subject_id: form.subject_id,
        schedule_slot_id: form.schedule_slot_id,
        status: form.status as AttendanceStatus,
        record_date: form.record_date || undefined,
      },
      { showError: true, showSuccess: true } as any
    );

    if (!dto) return false;
    attendanceForm.value.student_id = "";
    return true;
  } catch (err: any) {
    const m = extractPydanticValidationMessage(err);
    if (m) ElMessage.error(m);
    else reportError(err, "attendance.submit", "log");
    return false;
  }
}

function handleOpenAddDialog() {
  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return;
  }

  selectedAddSlot.value = null;

  attendanceForm.value = {
    student_id: "",
    status: "" as AttendanceStatus | "",
    record_date: selectedDate.value || todayISO,
    schedule_slot_id: String(selectedSlotFilterId.value || ""),
    subject_id: "",
  };

  addDialogVisible.value = true;
}

async function handleSaveAddDialog(payload: Partial<AttendanceFormModel>) {
  attendanceForm.value = { ...attendanceForm.value, ...payload };
  addDialogLoading.value = true;
  try {
    const ok = await submitAttendance();
    if (!ok) return;
    addDialogVisible.value = false;
    await loadAttendance(1);
  } finally {
    addDialogLoading.value = false;
  }
}

function handleCancelAddDialog() {
  addDialogVisible.value = false;
}

function openEditAttendanceDialog(row: AttendanceEnriched) {
  originalEditStatus.value = (row.status ?? "") as AttendanceStatus | "";

  editAttendanceForm.value = {
    attendance_id: String((row as any).id ?? (row as any)._id ?? ""),
    status: (row.status ?? "") as AttendanceStatus | "",
    student_name:
      row.student_name || String((row as any).student_id ?? "Unknown"),
  };

  editDialogVisible.value = true;
}

async function handleSaveEditDialog(payload: Partial<EditAttendanceFormModel>) {
  editAttendanceForm.value = { ...editAttendanceForm.value, ...payload };

  if (editAttendanceForm.value.status === originalEditStatus.value) {
    ElMessage.warning("Attendance not changed.");
    return;
  }

  editDialogLoading.value = true;
  try {
    await api.teacher.changeAttendanceStatus(
      editAttendanceForm.value.attendance_id,
      { new_status: editAttendanceForm.value.status as AttendanceStatus },
      { showError: true, showSuccess: true } as any
    );

    editDialogVisible.value = false;
    await loadAttendance(currentPage.value || 1);
  } catch (err) {
    reportError(err, "attendance.edit", "log");
  } finally {
    editDialogLoading.value = false;
  }
}

function handleCancelEditDialog() {
  editDialogVisible.value = false;
  originalEditStatus.value = "";
}

async function handleDeleteAttendance(row: AttendanceEnriched) {
  try {
    await ElMessageBox.confirm("Are you sure?", "Confirm", {
      type: "warning",
      confirmButtonText: "Yes",
    });

    const id = String((row as any).id ?? (row as any)._id ?? "");
    deleteLoadingId.value = id;

    await api.teacher.softDeleteAttendance(id, {
      showError: true,
      showSuccess: true,
    } as any);

    await loadAttendance(currentPage.value || 1);
  } catch (err) {
    // ignore cancel
  } finally {
    deleteLoadingId.value = null;
  }
}

/* ---------------- Header & Table ---------------- */
const { headerState } = useHeaderState({
  items: [
    {
      key: "total",
      getValue: () => statusSummary.value.total,
      singular: "record",
      plural: "records",
      variant: "primary",
      hideWhenZero: true,
    },
    {
      key: "present_rate",
      getValue: () => presentRate.value ?? 0,
      label: (value: number) =>
        presentRate.value === null ? undefined : `Present rate: ${value}%`,
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});

const attendanceColumns: ColumnConfig<AttendanceEnriched>[] = [
  {
    label: "Student",
    field: "student_name",
    render: (row) =>
      row.student_name ||
      String((row as AttendanceEnriched).student_id ?? "Unknown"),
  },
  {
    label: "Date",
    field: "record_date",
    render: (row) =>
      formatDate((row as AttendanceEnriched).record_date, "YYYY-MM-DD"),
  },
  {
    label: "Subject",
    field: "subject_label",
    render: (row) =>
      String(
        row.subject_label ?? (row as AttendanceEnriched).subject_id ?? "-"
      ),
  },
  {
    label: "Schedule",
    field: "schedule_slot_id",
    useSlot: true,
    slotName: "scheduleSlotLabel",
  },
  {
    label: "Status",
    field: "status",
    render: (row) => ({
      component: ElTag,
      componentProps: {
        type: getStatusTagType(String(row.status ?? "")),
        size: "small",
        effect: "plain",
      },
      value: row.status,
    }),
  },
  {
    label: "Updated",
    field: "lifecycle",
    render: (row) =>
      h(
        "span",
        { style: "font-size: 12px; color: var(--muted-color);" },
        formatDate(row.lifecycle?.updated_at)
      ),
  },
  {
    field: "id",
    operation: true,
    label: "Operation",
    align: "center",
    width: "220px",
  },
];

function isMySubject(row: AttendanceEnriched): boolean {
  const slotId = String(row.schedule_slot_id ?? "");
  return scheduleSlotMap.value.has(slotId);
}
const addDialogKey = computed(() => {
  return [
    "add",
    selectedClassId.value || "no-class",
    selectedDate.value || "no-date",
    addDialogVisible.value ? "open" : "closed",
  ].join("|");
});

const editDialogKey = computed(() => {
  return [
    "edit",
    editAttendanceForm.value.attendance_id || "no-id",
    editDialogVisible.value ? "open" : "closed",
  ].join("|");
});
</script>

<template>
  <div class="p-4 space-y-6" v-loading="tableLoading">
    <OverviewHeader
      title="Attendance"
      description="Mark and review attendance records."
      :loading="tableLoading"
      :showRefresh="false"
      :stats="headerState"
    >
      <template #filters>
        <el-form class="filters-form" label-position="top">
          <el-row :gutter="12" class="items-end">
            <!-- Class -->
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="Class">
                <TeacherClassSelect
                  v-model="selectedClassId"
                  placeholder="Select class"
                  class="w-full"
                />
              </el-form-item>
            </el-col>

            <!-- Date -->
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="Date">
                <ElDatePicker
                  v-model="selectedDate"
                  type="date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  class="w-full"
                  :disabledDate="(d: Date) => dayjs(d).isAfter(dayjs().tz('Asia/Phnom_Penh'), 'day')"
                />
              </el-form-item>
            </el-col>

            <!-- Slot (ensure full width) -->
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label="Schedule slot">
                <TeacherScheduleSlotSelect
                  v-model="selectedSlotFilterId"
                  :classId="selectedClassId || ''"
                  :date="selectedDate"
                  placeholder="All slots"
                  :disabled="!hasClassSelected"
                  class="w-full"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>

            <!-- Actions -->
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item label=" ">
                <div class="action-bar">
                  <BaseButton
                    type="primary"
                    :disabled="!hasClassSelected || hasNoSlotsForTeacher"
                    :loading="tableLoading"
                    @click="handleOpenAddDialog"
                  >
                    Mark attendance
                  </BaseButton>

                  <BaseButton
                    plain
                    :disabled="!hasClassSelected"
                    :loading="tableLoading"
                    @click="handleRefresh"
                  >
                    Refresh
                  </BaseButton>
                </div>
              </el-form-item>
            </el-col>

            <el-col
              v-if="hasNoSlotsForTeacher && hasClassSelected"
              :xs="24"
              class="mt-1"
            >
              <el-alert
                title="No Schedule Found"
                description="You are not scheduled to teach this class on the selected date."
                type="warning"
                show-icon
                :closable="false"
              />
            </el-col>
          </el-row>
        </el-form>
      </template>
    </OverviewHeader>

    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        @close="clearError"
      />
    </transition>

    <el-card v-if="isFirstLoad" shadow="never" class="rounded-xl">
      <el-skeleton animated :rows="7" />
    </el-card>

    <el-empty
      v-else-if="!hasClassSelected && !tableLoading"
      description="Select a class to view attendance."
      class="bg-white rounded-xl border"
    />

    <el-empty
      v-else-if="
        hasClassSelected && !tableLoading && attendanceList.length === 0
      "
      description="No attendance records for this date."
      class="bg-white rounded-xl border"
    />

    <template v-else>
      <el-row :gutter="16" class="items-stretch">
        <el-col :xs="12" :sm="6">
          <el-card shadow="hover" class="rounded-xl border">
            <div class="text-sm font-semibold text-[var(--muted-color)]">
              Total
            </div>
            <div class="text-2xl font-bold mt-1">{{ statusSummary.total }}</div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6">
          <el-card shadow="hover" class="rounded-xl border">
            <div class="text-sm font-semibold text-[var(--muted-color)]">
              Present
            </div>
            <div class="text-2xl font-bold mt-1">
              {{ statusSummary.present }}
            </div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6">
          <el-card shadow="hover" class="rounded-xl border">
            <div class="text-sm font-semibold text-[var(--muted-color)]">
              Absent
            </div>
            <div class="text-2xl font-bold mt-1">
              {{ statusSummary.absent }}
            </div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6">
          <el-card shadow="hover" class="rounded-xl border">
            <div class="text-sm font-semibold text-[var(--muted-color)]">
              Excused
            </div>
            <div class="text-2xl font-bold mt-1">
              {{ statusSummary.excused }}
            </div>
          </el-card>
        </el-col>
      </el-row>

      <TableCard
        title="Attendance records"
        description="Daily attendance log."
        :rightText="showingText"
      >
        <SmartTable
          :data="attendanceList"
          :columns="attendanceColumns"
          :loading="tableLoading"
        >
          <template #scheduleSlotLabel="{ row }">
            <div
              v-if="getSlotDisplay(row.schedule_slot_id)"
              class="leading-tight"
            >
              <div class="font-medium">
                {{
                  getSlotDisplay(row.schedule_slot_id)?.timeRange ||
                  getSlotDisplay(row.schedule_slot_id)?.label
                }}
              </div>
              <div
                v-if="getSlotDisplay(row.schedule_slot_id)?.room"
                class="text-xs text-[var(--muted-color)]"
              >
                Room: {{ getSlotDisplay(row.schedule_slot_id)?.room }}
              </div>
            </div>

            <div v-else class="leading-tight">
              <div class="font-medium text-[var(--text-color-regular)]">
                {{ row.subject_label || row.subject_id || "External Class" }}
              </div>
              <div class="text-xs text-[var(--muted-color)] italic">
                Diff. Schedule
              </div>
            </div>
          </template>

          <template #operation="{ row }">
            <div class="flex justify-center items-center gap-2">
              <ActionButtons
                v-if="isMySubject(row)"
                :rowId="String((row as any).id ?? (row as any)._id ?? '')"
                :detailContent="`Edit ${row.status}`"
                :deleteContent="`Remove record`"
                :detailLoading="isDetailLoading(String((row as any).id ?? (row as any)._id ?? ''))"
                :deleteLoading="isDeleteLoading(String((row as any).id ?? (row as any)._id ?? ''))"
                solid
                @detail="openEditAttendanceDialog(row)"
                @delete="handleDeleteAttendance(row)"
              />

              <template v-else>
                <el-tag type="info" size="small" effect="plain" class="italic">
                  Read Only
                </el-tag>
              </template>
            </div>
          </template>
        </SmartTable>

        <div
          v-if="Number(totalRows) > 0"
          class="mt-4 flex justify-end overflow-x-auto"
        >
          <el-pagination
            background
            layout="prev, pager, next, sizes, total"
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRows"
            @current-change="goPage"
            @size-change="
              (s) => {
                prefs.setTablePageSize(s);
                goPage(1);
              }
            "
          />
        </div>
      </TableCard>
    </template>

    <SmartFormDialog
      :key="addDialogKey"
      v-model:visible="addDialogVisible"
      v-model="attendanceForm"
      :fields="addAttendanceFields"
      title="Mark attendance"
      :loading="addDialogLoading"
      width="650px"
      @save="handleSaveAddDialog"
      @cancel="handleCancelAddDialog"
    />
    <SmartFormDialog
      :key="editDialogKey"
      v-model:visible="editDialogVisible"
      v-model="editAttendanceForm"
      :fields="editAttendanceFields"
      title="Edit attendance"
      :loading="editDialogLoading"
      width="500px"
      @save="handleSaveEditDialog"
      @cancel="handleCancelEditDialog"
    />
  </div>
</template>

<style scoped>
.filters-form :deep(.el-form-item) {
  margin-bottom: 0;
}

/* Slot + inputs full width inside form-item content */
.filters-form :deep(.el-form-item__content) {
  width: 100%;
}

/* Safety: any el-select inside filters grows */
.filters-form :deep(.el-select),
.filters-form :deep(.el-date-editor),
.filters-form :deep(.el-input) {
  width: 100%;
}

/* Optional: action bar spacing */
.action-bar {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
  flex-wrap: wrap;
}
</style>
