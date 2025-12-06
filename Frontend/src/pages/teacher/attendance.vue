<!-- ~/pages/teacher/attendance/index.vue -->
<script setup lang="ts">
definePageMeta({
  layout: "teacher",
});
import { ref, computed, watch } from "vue";
import {
  ElMessage,
  ElMessageBox,
  ElTag,
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
import ErrorBoundary from "~/components/error/ErrorBoundary.vue";

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

const loading = ref(false);
const errorMessage = ref<string | null>(null);

const selectedClassId = ref<string | null>(null);

const attendanceList = ref<AttendanceEnriched[]>([]);

/* ---------------- SmartTable columns ---------------- */

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

/* ---------------- helpers ---------------- */

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
  if (!selectedClassId.value) {
    attendanceList.value = [];
    return;
  }

  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await teacherApi.teacher.listAttendanceForClass(
      selectedClassId.value,
      { showError: false }
    );

    if (!res) {
      errorMessage.value = "Failed to load attendance.";
      attendanceList.value = [];
      return;
    }

    attendanceList.value = (res.items ?? []) as AttendanceEnriched[];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load attendance.";
  } finally {
    loading.value = false;
  }
};

/* ---------------- watch: when class changes ---------------- */

watch(
  () => selectedClassId.value,
  async () => {
    attendanceForm.value.student_id = "";
    attendanceList.value = [];

    if (!selectedClassId.value) return;
    await loadAttendance();
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

    await loadAttendance();
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
    ElMessage.success("Attendance updated.");
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

    ElMessage.success("Attendance record removed.");
  } catch {
    // cancelled
  }
};
</script>

<template>
  <div class="p-4 space-y-6">
    <!-- HEADER: gradient, consistent with other teacher pages -->
    <div
      class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-gradient-to-r from-[var(--color-primary-light-9)] to-[var(--color-primary-light-7)] rounded-2xl border border-[color:var(--color-primary-light-5)] shadow-sm p-5"
    >
      <div class="space-y-2">
        <h1
          class="text-2xl font-bold flex items-center gap-2 text-[color:var(--color-dark)]"
        >
          Attendance
        </h1>
        <p class="text-sm text-[color:var(--color-primary-light-1)]">
          Mark and review attendance records for your classes.
        </p>

        <div class="flex flex-wrap items-center gap-3">
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500">Class:</span>
            <TeacherClassSelect
              v-model="selectedClassId"
              placeholder="Select class"
              style="min-width: 220px"
            />
          </div>

          <div class="flex flex-wrap items-center gap-2 text-xs">
            <span
              v-if="statusSummary.total"
              class="inline-flex items-center gap-1 rounded-full bg-[var(--color-primary-light-8)] text-[color:var(--color-primary)] px-3 py-0.5 border border-[var(--color-primary-light-5)]"
            >
              <span
                class="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)]"
              />
              {{ statusSummary.total }}
              {{ statusSummary.total === 1 ? "record" : "records" }}
            </span>

            <span
              v-if="presentRate !== null"
              class="inline-flex items-center gap-1 rounded-full bg-white text-gray-700 px-3 py-0.5 border border-gray-200"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Present rate:
              <span class="font-medium">{{ presentRate }}%</span>
            </span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2 justify-end">
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
      </div>
    </div>

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
    <el-row :gutter="16" class="mt-2">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Total records</div>
          <div class="text-2xl font-semibold mt-1">
            {{ statusSummary.total }}
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="card-title">Present</div>
          <div class="text-2xl font-semibold mt-1 text-emerald-600">
            {{ statusSummary.present }}
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
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
      </ErrorBoundary>

      <div v-if="!loading && !filteredAttendance.length" class="py-10">
        <el-empty
          :description="
            selectedClassId
              ? 'No attendance records for this class yet'
              : 'Select a class to see attendance'
          "
          :image-size="120"
        >
          <template #extra>
            <p class="text-sm text-gray-500 max-w-md mx-auto">
              {{
                selectedClassId
                  ? "Use the Mark attendance button to create the first record."
                  : "Choose a class from the top to load its attendance records."
              }}
            </p>
          </template>
        </el-empty>
      </div>
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

<style scoped>
.stat-card {
  border-radius: 1rem;
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.card-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #9ca3af;
}
.el-card {
  transition: box-shadow 0.2s ease, transform 0.1s ease;
}
.el-card:hover {
  box-shadow: 0 4px 14px rgba(126, 87, 194, 0.12);
}

/* Table rounding */
:deep(.el-table) {
  border-radius: 0.75rem;
}
</style>
