<!-- ~/pages/teacher/attendance/index.vue -->
<script setup lang="ts">
definePageMeta({
  layout: "teacher",
});

import { ref, computed, watch } from "vue";
import {
  ElMessage,
  ElMessageBox,
  ElSelect,
  ElOption,
  ElInput,
  ElDatePicker,
} from "element-plus";

import { teacherService } from "~/api/teacher";
import type { AttendanceDTO, AttendanceStatus } from "~/api/types/school.dto";

import TeacherClassSelect from "~/components/Selects/TeacherClassSelect.vue";
import TeacherStudentSelect from "~/components/Selects/TeacherClassStudentSelect.vue";

import SmartTable from "~/components/TableEdit/core/SmartTable.vue";
import type { Field } from "~/components/types/form";
import SmartFormDialog from "~/components/Form/SmartFormDialog.vue";

import ActionButtons from "~/components/Button/ActionButtons.vue";
import BaseButton from "~/components/Base/BaseButton.vue";
import ErrorBoundary from "~/components/Error/ErrorBoundary.vue";
import OverviewHeader from "~/components/Overview/OverviewHeader.vue";

import { usePaginatedFetch } from "~/composables/usePaginatedFetch";
/* ---------------- SmartTable config ---------------- */
import { attendanceColumns } from "~/modules/tables/columns/teacher/attendanceColumns";

const teacherApi = teacherService();

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

const todayISO = new Date().toISOString().slice(0, 10);

/* ---------------- state ---------------- */

const selectedClassId = ref<string | null>(null);

/* ---------------- pagination + data (usePaginatedFetch) ---------------- */
const {
  data: attendanceList,
  loading,
  error,
  currentPage,
  pageSize,
  totalRows,
  fetchPage,
  goPage,
} = usePaginatedFetch<AttendanceEnriched, string | null>(
  async (classId, page, pageSize, signal) => {
    if (!classId) {
      return { items: [], total: 0 };
    }

    const res = await teacherApi.teacher.listAttendanceForClass(classId, {
      page,
      page_size: pageSize,
      signal,
      showError: false,
    });

    const allItems = (res?.items ?? []) as AttendanceEnriched[];
    const total = res?.total ?? allItems.length;

    // FRONTEND SLICE (fake pagination until backend is ready)
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const pageItems = allItems.slice(start, end);

    return {
      items: pageItems,
      total,
    };
  },
  1,
  10,
  selectedClassId
);
/* error message mapped from hook error */
const errorMessage = computed<string | null>(() =>
  error.value ? error.value.message ?? "Failed to load attendance." : null
);

/* ---------------- SmartTable forms ---------------- */

// create (mark) attendance
const attendanceForm = ref<AttendanceFormModel>({
  student_id: "",
  status: "" as AttendanceStatus | "",
  record_date: todayISO,
});

// edit attendance
const editAttendanceForm = ref<EditAttendanceFormModel>({
  attendance_id: "",
  status: "" as AttendanceStatus | "",
  student_name: "",
});

const addDialogVisible = ref(false);
const addDialogLoading = ref(false);

const editDialogVisible = ref(false);
const editDialogLoading = ref(false);

/* ---------------- computed ---------------- */

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

// filtered by selected student (using form.student_id as simple filter)
const filteredAttendance = computed(() => {
  const sId = attendanceForm.value.student_id;
  if (!sId) return attendanceList.value;
  return attendanceList.value.filter((a) => a.student_id === sId);
});

const canRefresh = computed(() => !!selectedClassId.value && !loading.value);

/* ---------------- SmartForm fields (dialogs) ---------------- */

// Create / mark attendance
const addAttendanceFields = computed<Field<AttendanceFormModel>[]>(() => [
  {
    key: "student_id",
    label: "Student",
    component: TeacherStudentSelect,
    componentProps: {
      classId: selectedClassId.value || "",
      reload: true,
      valueKey: "id",
      labelKey: "username",
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
    componentProps: {
      placeholder: "Select status",
      style: "width: 100%",
    },
  },
  {
    key: "record_date",
    label: "Date",
    component: ElDatePicker,
    componentProps: {
      type: "date",
      valueFormat: "YYYY-MM-DD",
      placeholder: "Pick a day",
      style: "width: 100%",
      disabledDate: (date: Date) => {
        // disable any date strictly in the future
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const candidate = new Date(date);
        candidate.setHours(0, 0, 0, 0);

        return candidate.getTime() > today.getTime();
      },
    },
  },
]);

// Edit attendance (status only)
const editAttendanceFields: Field<EditAttendanceFormModel>[] = [
  {
    key: "student_name",
    label: "Student",
    component: ElInput,
    formItemProps: {
      required: false,
    },
    componentProps: {
      disabled: true,
      placeholder: "Student name",
    },
  },
  {
    key: "attendance_id",
    label: "Record ID",
    component: ElInput,
    componentProps: {
      disabled: true,
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
    componentProps: {
      placeholder: "Select status",
      style: "width: 100%",
    },
  },
];

/* ---------------- api: load attendance ---------------- */

const loadAttendance = async () => {
  await fetchPage(currentPage.value || 1);
};

/* ---------------- watch: when class changes ---------------- */

watch(
  () => selectedClassId.value,
  async (val) => {
    attendanceForm.value.student_id = "";

    if (!val) {
      // clear when no class selected
      attendanceList.value = [];
      totalRows.value = 0;
      return;
    }

    // when class changes, always go back to page 1
    await fetchPage(1);
  }
);

/* ---------------- create: mark attendance ---------------- */
const submitAttendance = async () => {
  const form = attendanceForm.value;

  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return;
  }
  if (!form.student_id || !form.status) {
    ElMessage.warning("Student and status are required.");
    return;
  }

  try {
    const dto = await teacherApi.teacher.markAttendance(
      {
        student_id: form.student_id,
        class_id: selectedClassId.value,
        status: form.status as AttendanceStatus,
        record_date: form.record_date || undefined,
      },
      { showError: false }
    );

    if (!dto) {
      ElMessage.error("Failed to record attendance.");
      return;
    }

    // reload list
    await loadAttendance();

    attendanceForm.value.student_id = "";

    ElMessage.success("Attendance recorded.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to record attendance.");
  }
};

const handleOpenAddDialog = () => {
  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return;
  }

  attendanceForm.value = {
    student_id: "",
    status: "" as AttendanceStatus | "",
    record_date: todayISO,
  };

  addDialogVisible.value = true;
};

const handleSaveAddDialog = async (payload: Partial<AttendanceFormModel>) => {
  attendanceForm.value = { ...attendanceForm.value, ...payload };
  addDialogLoading.value = true;
  try {
    await submitAttendance();
    addDialogVisible.value = false;
  } finally {
    addDialogLoading.value = false;
  }
};

const handleCancelAddDialog = () => {
  addDialogVisible.value = false;
};

/* ---------------- edit: change status ---------------- */

const openEditAttendanceDialog = (row: AttendanceEnriched) => {
  editAttendanceForm.value = {
    attendance_id: row.id,
    status: row.status,
    student_name: row.student_name || row.student_id || "Unknown",
  };
  editDialogVisible.value = true;
};

const submitEditAttendance = async () => {
  const form = editAttendanceForm.value;
  if (!form.attendance_id || !form.status) {
    ElMessage.warning("Record ID and status are required.");
    return;
  }

  try {
    const dto = await teacherApi.teacher.changeAttendanceStatus(
      form.attendance_id,
      { new_status: form.status as AttendanceStatus },
      { showError: false }
    );

    if (!dto) {
      ElMessage.error("Failed to update status.");
      return;
    }
    await loadAttendance();
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to update status.");
  }
};

const handleSaveEditDialog = async (
  payload: Partial<EditAttendanceFormModel>
) => {
  editAttendanceForm.value = { ...editAttendanceForm.value, ...payload };
  editDialogLoading.value = true;
  try {
    await submitEditAttendance();
    editDialogVisible.value = false;
  } finally {
    editDialogLoading.value = false;
  }
};

const handleCancelEditDialog = () => {
  editDialogVisible.value = false;
};

/* ---------------- delete: future remove ---------------- */

const handleDeleteAttendance = async (row: AttendanceEnriched) => {
  try {
    await ElMessageBox.confirm(
      "Are you sure you want to remove this attendance record?",
      "Confirm",
      {
        type: "warning",
        confirmButtonText: "Yes",
        cancelButtonText: "No",
      }
    );

    // TODO: when backend is ready:
    // await teacherApi.teacher.deleteAttendance(row.id, { showError: false });

    attendanceList.value = attendanceList.value.filter((a) => a.id !== row.id);
  } catch {
    // cancelled
  }
};

/* ---------------- pagination handlers ---------------- */

const handlePageChange = (page: number) => {
  goPage(page);
};

const handlePageSizeChange = (size: number) => {
  pageSize.value = size;
  fetchPage(1);
};
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
      label: (value) =>
        presentRate.value === null ? undefined : `Present rate: ${value}%`,
      variant: "secondary",
      dotClass: "bg-emerald-500",
      hideWhenZero: true,
    },
  ],
});
</script>

<template>
  <div class="p-4 space-y-6">
    <!-- HEADER -->
    <OverviewHeader
      title="Attendance"
      description="Mark and review attendance records for your classes."
      :loading="loading"
      :showRefresh="false"
      :stats="headerState"
    >
      <!-- Under title: class select (filters slot) -->
      <template #filters>
        <div class="flex flex-wrap items-center gap-3 mb-3">
          <div
            class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/90 border border-[var(--color-primary-light-7)] shadow-sm"
          >
            <span class="text-xs font-medium text-[color:var(--color-primary)]">
              Class:
            </span>
            <TeacherClassSelect
              v-model="selectedClassId"
              placeholder="Select class"
              style="min-width: 220px"
              class="header-class-select"
            />
          </div>
        </div>
      </template>

      <!-- Right side: custom actions -->
      <template #actions>
        <BaseButton
          plain
          :loading="loading"
          :disabled="!canRefresh"
          class="!border-[color:var(--color-primary)] !text-[color:var(--color-primary)] hover:!bg-[var(--color-primary-light-7)]"
          @click="loadAttendance"
        >
          Refresh
        </BaseButton>

        <BaseButton
          type="primary"
          :disabled="!selectedClassId"
          :loading="loading"
          @click="handleOpenAddDialog"
        >
          Mark attendance
        </BaseButton>
      </template>
    </OverviewHeader>

    <!-- ERROR -->
    <transition name="el-fade-in">
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        closable
        class="rounded-xl border border-red-200/60 shadow-sm"
        @close="errorMessage = null"
      />
    </transition>

    <!-- SUMMARY CARDS -->
    <el-row :gutter="16" class="mt-2 items-stretch">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card h-full">
          <div class="card-title">Total records</div>
          <div class="text-2xl font-semibold mt-1">
            {{ statusSummary.total }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card h-full">
          <div class="card-title">Present</div>
          <div class="text-2xl font-semibold mt-1 text-emerald-600">
            {{ statusSummary.present }}
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card h-full">
          <div class="card-title">Absent / Excused</div>
          <div class="text-sm mt-1">
            <span class="text-red-500 font-semibold">
              {{ statusSummary.absent }}
            </span>
            <span class="mx-1 text-gray-400">/</span>
            <span class="text-amber-600 font-semibold">
              {{ statusSummary.excused }}
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- TABLE CARD -->
    <el-card
      shadow="never"
      :body-style="{ padding: '20px' }"
      class="rounded-2xl border border-gray-200/60 shadow-sm bg-white mt-4"
    >
      <template #header>
        <div
          class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2"
        >
          <div>
            <div class="text-base font-semibold text-gray-800">
              Attendance records
            </div>
            <p class="text-xs text-gray-500">
              Each row is one record for a given student and date.
            </p>
          </div>

          <div class="flex items-center gap-2 text-xs text-gray-500">
            <span>
              Showing {{ filteredAttendance.length }} /
              {{ attendanceList.length }} records
            </span>
          </div>
        </div>
      </template>

      <ErrorBoundary>
        <SmartTable
          :data="filteredAttendance"
          :columns="attendanceColumns"
          :loading="loading"
          :smartProps="{
            border: true,
            size: 'small',
            'highlight-current-row': true,
          }"
        >
          <template #operation="{ row }">
            <ActionButtons
              :rowId="row.id"
              :detailContent="`Edit ${row.status}`"
              :deleteContent="`Remove record`"
              @detail="openEditAttendanceDialog(row)"
              @delete="handleDeleteAttendance(row)"
            />
          </template>
        </SmartTable>

        <!-- Pagination -->
        <div v-if="totalRows > 0" class="mt-4 flex justify-end">
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
      </ErrorBoundary>
    </el-card>

    <!-- CREATE / MARK ATTENDANCE DIALOG -->
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

    <!-- EDIT ATTENDANCE DIALOG -->
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
