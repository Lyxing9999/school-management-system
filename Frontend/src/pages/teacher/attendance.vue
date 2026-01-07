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
} from "element-plus";

import dayjs from "dayjs";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
dayjs.extend(utc);
dayjs.extend(timezone);

import { teacherService } from "~/api/teacher";
import type { AttendanceDTO, AttendanceStatus } from "~/api/types/school.dto";

import TeacherClassSelect from "~/components/selects/class/TeacherClassSelect.vue";
import TeacherStudentSelect from "~/components/selects/subject/TeacherClassStudentSelect.vue";

import SmartTable from "~/components/table-edit/core/table/SmartTable.vue";
import type { Field } from "~/components/types/form";
import SmartFormDialog from "~/components/form/SmartFormDialog.vue";

import ActionButtons from "~/components/buttons/ActionButtons.vue";
import BaseButton from "~/components/base/BaseButton.vue";
import OverviewHeader from "~/components/overview/OverviewHeader.vue";
import TableCard from "~/components/cards/TableCard.vue";

import { usePaginatedFetch } from "~/composables/data/usePaginatedFetch";
import { useHeaderState } from "~/composables/ui/useHeaderState";

import { usePreferencesStore } from "~/stores/preferencesStore";
import { formatDate } from "~/utils/date/formatDate";
import type { ColumnConfig } from "~/components/types/tableEdit";

import { reportError } from "~/utils/errors/errors";

const api = teacherService();
const prefs = usePreferencesStore();
const { tablePageSize } = storeToRefs(prefs);

/* ---------------- types ---------------- */
type AttendanceEnriched = AttendanceDTO & {
  student_name?: string;
  class_name?: string;
  teacher_name?: string;
};

type AttendanceFormModel = {
  student_id: string;
  status: AttendanceStatus | "";
  record_date: string;
};

type EditAttendanceFormModel = {
  student_name: string;
  attendance_id: string;
  status: AttendanceStatus | "";
};

/* ---------------- constants ---------------- */
const todayISO = dayjs().tz("Asia/Phnom_Penh").format("YYYY-MM-DD");

/* ---------------- filters ---------------- */
const selectedClassId = ref<string | null>(null);
const selectedDate = ref<string>(todayISO);

/* ---------------- helpers ---------------- */
function getStatusTagType(status: string) {
  if (status === "present") return "success";
  if (status === "excused") return "warning";
  return "danger";
}

/* ---------------- per-row loading ---------------- */
const detailLoadingId = ref<string | null>(null);
const deleteLoadingId = ref<string | null>(null);

const isDetailLoading = (id: string) => detailLoadingId.value === id;
const isDeleteLoading = (id: string) => deleteLoadingId.value === id;

/* ---------------- paginated fetch ----------------
   Backend list endpoint has NO page/page_size
   => fetch all items for (class_id, date) and slice on frontend
*/
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
  { classId: string | null; date: string }
>(
  async (filter, page, size, signal) => {
    const classId = filter?.classId;
    const date = filter?.date;

    if (!classId) return { items: [], total: 0 };

    // IMPORTANT: pass { date } so backend filters by day
    const res: any = await api.teacher.listAttendanceForClass(classId, {
      date,
    });

    // callApi usually returns { data, error } shape; keep defensive parsing
    const payload = res?.data?.data ?? res?.data ?? res;

    const allItems = (payload?.items ?? []) as AttendanceEnriched[];

    // optional sort newest first
    const sorted = allItems.slice().sort((a: any, b: any) => {
      const ad = new Date(a?.record_date ?? a?.date ?? 0).getTime();
      const bd = new Date(b?.record_date ?? b?.date ?? 0).getTime();
      return bd - ad;
    });

    const total = Number(payload?.total ?? sorted.length);
    const start = (page - 1) * size;
    const end = start + size;

    return { items: sorted.slice(start, end), total };
  },
  {
    initialPage: 1,
    pageSizeRef: tablePageSize,
    filter: computed(() => ({
      classId: selectedClassId.value,
      date: selectedDate.value,
    })),
  }
);

const tableLoading = computed(() => initialLoading.value || fetching.value);

/* ---------------- error ---------------- */
const errorMessage = computed(() =>
  tableError.value
    ? tableError.value.message ?? "Failed to load attendance."
    : null
);

function clearError() {
  // no-op
}

/* ---------------- forms ---------------- */
const attendanceForm = ref<AttendanceFormModel>({
  student_id: "",
  status: "" as AttendanceStatus | "",
  record_date: todayISO,
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

/* ---------------- computed ---------------- */
const hasClassSelected = computed(() => !!selectedClassId.value);
const canRefresh = computed(
  () => !!selectedClassId.value && !tableLoading.value
);

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

/* ---------------- SmartForm fields ---------------- */
const addAttendanceFields = computed<Field<AttendanceFormModel>[]>(() => [
  {
    key: "student_id",
    label: "Student",
    component: TeacherStudentSelect,
    componentProps: {
      classId: selectedClassId.value || "",
      reload: true,
      multiple: false,
      placeholder: "Select student",
      disabled: !selectedClassId.value,
    },
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
  {
    key: "record_date",
    label: "Date",
    component: ElDatePicker,
    componentProps: {
      type: "date",
      format: "YYYY-MM-DD",
      valueFormat: "YYYY-MM-DD",
      placeholder: "Pick a day",
      style: "width: 100%",
      disabledDate: (date: Date) => {
        const todayKh = dayjs().tz("Asia/Phnom_Penh").startOf("day");
        const candidate = dayjs(date).startOf("day");
        return candidate.isAfter(todayKh);
      },
    },
  },
]);

const editAttendanceFields: Field<EditAttendanceFormModel>[] = [
  {
    key: "student_name",
    label: "Student",
    component: ElInput,
    formItemProps: { required: false },
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

/* ---------------- api helpers ---------------- */
async function loadAttendance(page = currentPage.value || 1) {
  await fetchPage(page);
}

/* ---------------- watch: class/date change ---------------- */
watch(
  () => [selectedClassId.value, selectedDate.value],
  async () => {
    // keep add form date in sync with filter date
    attendanceForm.value.record_date = selectedDate.value || todayISO;
    attendanceForm.value.student_id = "";
    goPage(1);
  }
);

/* ---------------- create ---------------- */
async function submitAttendance(): Promise<boolean> {
  const form = attendanceForm.value;

  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return false;
  }

  if (!form.student_id || !form.status) {
    ElMessage.warning("Student and status are required.");
    return false;
  }

  try {
    const dto = await api.teacher.markAttendance(
      {
        student_id: form.student_id,
        class_id: selectedClassId.value,
        status: form.status as AttendanceStatus,
        record_date: form.record_date || undefined,
      },
      { showError: false, showSuccess: true } as any
    );

    if (!dto) {
      ElMessage.error("Failed to record attendance.");
      return false;
    }

    attendanceForm.value.student_id = "";
    return true;
  } catch (err) {
    reportError(err, "attendance.submit", "log");
    return false;
  }
}

function handleOpenAddDialog() {
  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return;
  }

  attendanceForm.value = {
    student_id: "",
    status: "" as AttendanceStatus | "",
    record_date: selectedDate.value || todayISO,
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

/* ---------------- edit ---------------- */
function openEditAttendanceDialog(row: AttendanceEnriched) {
  originalEditStatus.value = (row.status ?? "") as AttendanceStatus | "";

  editAttendanceForm.value = {
    attendance_id: String((row as any).id ?? row._id ?? ""),
    status: (row.status ?? "") as AttendanceStatus | "",
    student_name: row.student_name || (row as any).student_id || "Unknown",
  };

  editDialogVisible.value = true;
}

async function submitEditAttendance() {
  const form = editAttendanceForm.value;

  if (!form.attendance_id || !form.status) {
    ElMessage.warning("Record ID and status are required.");
    return;
  }

  try {
    const dto = await api.teacher.changeAttendanceStatus(
      form.attendance_id,
      { new_status: form.status as AttendanceStatus },
      { showError: false, showSuccess: true } as any
    );

    if (!dto) {
      ElMessage.error("Failed to update status.");
      return;
    }

    await loadAttendance(currentPage.value || 1);
  } catch (err) {
    reportError(err, "attendance.edit", "log");
  }
}

async function handleSaveEditDialog(payload: Partial<EditAttendanceFormModel>) {
  editAttendanceForm.value = { ...editAttendanceForm.value, ...payload };

  if (editAttendanceForm.value.status === originalEditStatus.value) {
    ElMessage.warning("Attendance not changed (same status).");
    return;
  }

  editDialogLoading.value = true;
  try {
    await submitEditAttendance();
    editDialogVisible.value = false;
  } finally {
    editDialogLoading.value = false;
  }
}

function handleCancelEditDialog() {
  editDialogVisible.value = false;
  originalEditStatus.value = "";
}

/* ---------------- delete (soft delete) ---------------- */
async function handleDeleteAttendance(row: AttendanceEnriched) {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to remove this attendance record?",
      "Confirm",
      { type: "warning", confirmButtonText: "Yes", cancelButtonText: "No" }
    );

    const id = String((row as any).id ?? row._id ?? "");
    if (!id) {
      ElMessage.error("Missing attendance id.");
      return;
    }

    deleteLoadingId.value = id;

    const res = await api.teacher.softDeleteAttendance(id, {
      showError: false,
      showSuccess: true,
    } as any);

    if (!res) {
      ElMessage.error("Failed to delete attendance.");
      return;
    }

    // After delete, reload current page (or goPage(1) if you prefer)
    await loadAttendance(currentPage.value || 1);
  } catch (err) {
    reportError(err, "attendance.softDelete", "log");
  } finally {
    deleteLoadingId.value = null;
  }
}

/* ---------------- pagination ---------------- */
function handlePageChange(page: number) {
  goPage(page);
}

function handlePageSizeChange(size: number) {
  prefs.setTablePageSize(size);
  goPage(1);
}

/* ---------------- header stats ---------------- */
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

/* ---------------- table columns ---------------- */
const attendanceColumns: ColumnConfig<AttendanceEnriched>[] = [
  {
    label: "Student",
    field: "student_name",
    render: (row: AttendanceEnriched) =>
      row.student_name || (row as any).student_id || "Unknown",
  },
  {
    label: "Date",
    field: "record_date",
    render: (row: AttendanceEnriched) =>
      formatDate((row as any).record_date ?? (row as any).date, "YYYY-MM-DD"),
  },
  {
    label: "Status",
    field: "status",
    render: (row: AttendanceEnriched) => ({
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
    label: "Created",
    field: "lifecycle.created_at",
    render: (row: AttendanceEnriched) => ({
      component: "span",
      componentProps: { style: "font-size: 12px; color: var(--muted-color);" },
      value: formatDate((row as any).lifecycle?.created_at),
    }),
  },
  {
    label: "Updated",
    field: "lifecycle.updated_at",
    render: (row: AttendanceEnriched) => ({
      component: "span",
      componentProps: { style: "font-size: 12px; color: var(--muted-color);" },
      value: formatDate((row as any).lifecycle?.updated_at),
    }),
  },
  {
    field: "id",
    operation: true,
    label: "Operation",
    inlineEditActive: false,
    align: "center",
    width: "220px",
    smartProps: {},
  },
];
</script>

<template>
  <div class="attendance-page" v-loading="tableLoading">
    <OverviewHeader
      title="Attendance"
      description="Mark and review attendance records for your classes."
      :loading="tableLoading"
      :showRefresh="false"
      :stats="headerState"
    >
      <template #filters>
        <div class="header-filters">
          <div class="filter-pill">
            <span class="filter-pill__label">Class</span>
            <TeacherClassSelect
              v-model="selectedClassId"
              placeholder="Select class"
              class="header-class-select"
            />
          </div>

          <div class="filter-pill">
            <span class="filter-pill__label">Date</span>
            <ElDatePicker
              v-model="selectedDate"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              placeholder="Pick a day"
              class="header-date-select"
              :disabledDate="(d: Date) => dayjs(d).isAfter(dayjs().tz('Asia/Phnom_Penh'), 'day')"
            />
          </div>
        </div>
      </template>

      <template #actions>
        <div class="header-actions">
          <BaseButton
            plain
            :loading="tableLoading"
            :disabled="!canRefresh"
            class="btn-soft-primary"
            @click="loadAttendance(1)"
          >
            Refresh
          </BaseButton>

          <BaseButton
            type="primary"
            :disabled="!hasClassSelected"
            :loading="tableLoading"
            @click="handleOpenAddDialog"
          >
            Mark attendance
          </BaseButton>
        </div>
      </template>
    </OverviewHeader>

    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="state-alert"
        @close="clearError"
      />
    </transition>

    <!-- First load skeleton -->
    <el-card v-if="isFirstLoad" shadow="never" class="state-card">
      <el-skeleton animated :rows="7" />
    </el-card>

    <!-- No class selected -->
    <el-card
      v-else-if="!hasClassSelected && !tableLoading"
      shadow="never"
      class="state-card"
    >
      <el-empty
        description="Select a class to view attendance."
        class="empty-compact"
      />
    </el-card>

    <!-- Class selected but no records -->
    <el-card
      v-else-if="
        hasClassSelected && !tableLoading && attendanceList.length === 0
      "
      shadow="never"
      class="state-card"
    >
      <el-empty
        description="No attendance records for this date."
        class="empty-compact"
      />
    </el-card>

    <!-- Content -->
    <template v-else>
      <el-row :gutter="16" class="items-stretch summary-row">
        <el-col :xs="12" :sm="6">
          <el-card shadow="hover" class="stat-card h-full">
            <div class="card-title">Total</div>
            <div class="stat-value">{{ statusSummary.total }}</div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6">
          <el-card shadow="hover" class="stat-card h-full">
            <div class="card-title">Present</div>
            <div class="stat-value">{{ statusSummary.present }}</div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6">
          <el-card shadow="hover" class="stat-card h-full">
            <div class="card-title">Absent</div>
            <div class="stat-value">{{ statusSummary.absent }}</div>
          </el-card>
        </el-col>

        <el-col :xs="12" :sm="6">
          <el-card shadow="hover" class="stat-card h-full">
            <div class="card-title">Excused</div>
            <div class="stat-value">{{ statusSummary.excused }}</div>
          </el-card>
        </el-col>
      </el-row>

      <TableCard
        title="Attendance records"
        description="Each row is one record for a student and date."
        :padding="'20px'"
        :rightText="showingText"
      >
        <div class="table-x">
          <SmartTable
            :data="attendanceList"
            :columns="attendanceColumns"
            :loading="tableLoading"
          >
            <template #operation="{ row }">
              <div class="op-wrap">
                <ActionButtons
                  :rowId="String((row as any).id ?? row._id ?? '')"
                  :detailContent="`Edit ${row.status}`"
                  :deleteContent="`Remove record`"
                  :detailLoading="isDetailLoading(String((row as any).id ?? row._id ?? ''))"
                  :deleteLoading="isDeleteLoading(String((row as any).id ?? row._id ?? ''))"
                  solid
                  @detail="openEditAttendanceDialog(row)"
                  @delete="handleDeleteAttendance(row)"
                />
              </div>
            </template>
          </SmartTable>
        </div>

        <div v-if="Number(totalRows) > 0" class="pagination-wrap">
          <el-pagination
            background
            layout="prev, pager, next, jumper, sizes, total"
            :current-page="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRows"
            @current-change="handlePageChange"
            @size-change="handlePageSizeChange"
          />
        </div>
      </TableCard>
    </template>

    <!-- CREATE / MARK -->
    <SmartFormDialog
      v-model:visible="addDialogVisible"
      v-model="attendanceForm"
      :fields="addAttendanceFields"
      title="Mark attendance"
      :loading="addDialogLoading"
      :width="'600px'"
      @save="handleSaveAddDialog"
      @cancel="handleCancelAddDialog"
    />

    <!-- EDIT -->
    <SmartFormDialog
      v-model:visible="editDialogVisible"
      v-model="editAttendanceForm"
      :fields="editAttendanceFields"
      title="Edit attendance"
      :loading="editDialogLoading"
      :width="'500px'"
      @save="handleSaveEditDialog"
      @cancel="handleCancelEditDialog"
    />
  </div>
</template>

<style scoped>
.attendance-page {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-filters {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.header-actions {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.state-card {
  border-radius: 14px !important;
  border: 1px solid var(--border-color) !important;
  background: color-mix(
    in srgb,
    var(--color-card) 92%,
    var(--color-bg) 8%
  ) !important;
}

.state-alert {
  border-radius: 14px !important;
  border: 1px solid
    color-mix(in srgb, var(--el-color-danger) 22%, var(--border-color) 78%) !important;
  background: color-mix(
    in srgb,
    var(--el-color-danger) 6%,
    var(--color-card) 94%
  ) !important;
}

.btn-soft-primary {
  border: 1px solid
    color-mix(in srgb, var(--color-primary) 40%, var(--border-color) 60%) !important;
  color: var(--color-primary) !important;
  background: transparent !important;
}

.filter-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  border-radius: 9999px;
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--hover-bg) 55%, transparent);
}

.filter-pill__label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-primary);
}

.header-class-select {
  min-width: 220px;
}

.header-date-select {
  width: 160px;
}

.summary-row {
  align-items: stretch;
}

.stat-card {
  border-radius: 14px;
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--color-card) 92%, var(--color-bg) 8%);
}

.card-title {
  color: var(--muted-color);
  font-size: 0.875rem;
  font-weight: 600;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 0.25rem;
  color: var(--text-color);
}

.table-x {
  width: 100%;
  min-width: 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table-x :deep(.el-table) {
  min-width: 820px;
}

.op-wrap {
  display: flex;
  justify-content: center;
}

.pagination-wrap {
  margin-top: 14px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .attendance-page {
    padding: 12px;
    gap: 14px;
  }

  .header-class-select {
    width: 100%;
    min-width: 0 !important;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions :deep(button) {
    width: 100%;
  }

  :deep(.el-card__body) {
    padding: 14px !important;
  }

  .stat-value {
    font-size: 1.25rem;
  }

  .pagination-wrap {
    justify-content: stretch;
  }

  :deep(.el-pagination) {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: flex-end;
  }
}
</style>
