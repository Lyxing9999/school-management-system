<!-- ~/pages/teacher/attendance/index.vue -->
<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { ElMessage } from "element-plus";

import { teacherService } from "~/api/teacher";
import type { AttendanceDTO, AttendanceStatus } from "~/api/types/school.dto";

definePageMeta({
  layout: "teacher",
});

const teacherApi = teacherService();

// ---------------- types ----------------

interface ClassOption {
  id: string;
  name: string;
}

interface StudentOption {
  id: string;
  username: string;
}

interface AttendanceForm {
  student_id: string;
  status: AttendanceStatus | "";
  record_date: string; // YYYY-MM-DD
}

const todayISO = new Date().toISOString().slice(0, 10);

// ---------------- state ----------------

const loading = ref(false);
const errorMessage = ref<string | null>(null);

const classOptions = ref<ClassOption[]>([]);
const selectedClassId = ref<string | null>(null);

const studentOptions = ref<StudentOption[]>([]);
const attendanceList = ref<AttendanceDTO[]>([]);

const attendanceForm = ref<AttendanceForm>({
  student_id: "",
  status: "" as AttendanceStatus | "",
  record_date: todayISO,
});

// ---------------- computed ----------------

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

const filteredAttendance = computed(() => {
  const sId = attendanceForm.value.student_id;
  if (!sId) return attendanceList.value;
  return attendanceList.value.filter((a) => a.student_id === sId);
});

const canRefresh = computed(
  () =>
    !!selectedClassId.value && !loading.value && classOptions.value.length > 0
);

// ---------------- helpers ----------------

const getStatusTagType = (status: AttendanceStatus) => {
  if (status === "present") return "success";
  if (status === "excused") return "warning";
  return "danger"; // absent
};

const formatDate = (value?: string | null) => {
  if (!value) return "-";
  // assuming backend returns ISO string; keep only date part
  return value.slice(0, 10);
};

// ---------------- api calls ----------------

const loadClassOptions = async () => {
  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await teacherApi.teacher.listClassNameSelect();
    const items = res?.items ?? [];

    classOptions.value = items.map((c: any) => ({
      id: c.id,
      name: c.name,
    }));

    if (!selectedClassId.value && classOptions.value.length > 0) {
      selectedClassId.value = classOptions.value[0].id;
    }
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load classes.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

const loadStudentOptions = async (classId: string | null) => {
  if (!classId) {
    studentOptions.value = [];
    return;
  }

  try {
    const res = await teacherApi.teacher.listStudentsInClass(classId);
    const items = res?.items ?? [];
    studentOptions.value = items.map((s: any) => ({
      id: s.id,
      username: s.username,
    }));
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to load students.");
  }
};

const loadAttendance = async () => {
  if (!selectedClassId.value) {
    attendanceList.value = [];
    return;
  }

  loading.value = true;
  errorMessage.value = null;

  try {
    const res = await teacherApi.teacher.listAttendanceForClass(
      selectedClassId.value
    );
    attendanceList.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load attendance.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

// when class changes => reset student, reload students + attendance
watch(
  () => selectedClassId.value,
  async (newId) => {
    attendanceForm.value.student_id = "";
    studentOptions.value = [];
    attendanceList.value = [];

    if (!newId) return;
    await Promise.all([loadStudentOptions(newId), loadAttendance()]);
  }
);

// initial load
onMounted(async () => {
  await loadClassOptions();
  if (selectedClassId.value) {
    await Promise.all([
      loadStudentOptions(selectedClassId.value),
      loadAttendance(),
    ]);
  }
});

// ---------------- actions ----------------

const submitAttendance = async () => {
  if (!selectedClassId.value) {
    ElMessage.warning("Please select a class first.");
    return;
  }
  if (!attendanceForm.value.student_id || !attendanceForm.value.status) {
    ElMessage.warning("Student and status are required.");
    return;
  }

  try {
    const dto = await teacherApi.teacher.markAttendance({
      student_id: attendanceForm.value.student_id,
      class_id: selectedClassId.value,
      status: attendanceForm.value.status as AttendanceStatus,
      record_date: attendanceForm.value.record_date || undefined,
    });

    attendanceList.value.unshift(dto);
    ElMessage.success("Attendance recorded.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to record attendance.");
  }
};

const quickChangeAttendanceStatus = async (
  attendanceId: string,
  newStatus: AttendanceStatus
) => {
  try {
    const dto = await teacherApi.teacher.changeAttendanceStatus(attendanceId, {
      new_status: newStatus,
    });
    const idx = attendanceList.value.findIndex((a) => a.id === dto.id);
    if (idx !== -1) attendanceList.value[idx] = dto;
    ElMessage.success("Attendance updated.");
  } catch (err: any) {
    console.error(err);
    ElMessage.error(err?.message ?? "Failed to update status.");
  }
};
</script>

<template>
  <div class="p-4 space-y-6">
    <!-- HEADER -->
    <el-row justify="space-between" align="middle">
      <el-col :span="12">
        <h1 class="text-xl font-semibold mb-2">Attendance</h1>

        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-500">Class:</span>
          <el-select
            v-model="selectedClassId"
            placeholder="Select class"
            size="small"
            style="min-width: 220px"
            :disabled="!classOptions.length"
            clearable
          >
            <el-option
              v-for="c in classOptions"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </div>
      </el-col>

      <el-col :span="12" class="text-right">
        <el-button
          type="primary"
          :loading="loading"
          :disabled="!canRefresh"
          @click="loadAttendance"
        >
          Refresh
        </el-button>
      </el-col>
    </el-row>

    <!-- ERROR -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mt-2"
    />

    <!-- SKELETON -->
    <el-skeleton v-if="loading" :rows="4" animated />

    <template v-else>
      <!-- SUMMARY -->
      <el-row :gutter="16">
        <el-col :xs="24" :sm="8">
          <el-card shadow="hover">
            <div class="text-xs text-gray-500">Total records</div>
            <div class="text-2xl font-semibold mt-1">
              {{ statusSummary.total }}
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card shadow="hover">
            <div class="text-xs text-gray-500">Present</div>
            <div class="text-2xl font-semibold mt-1 text-green-600">
              {{ statusSummary.present }}
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-card shadow="hover">
            <div class="text-xs text-gray-500">Absent / Excused</div>
            <div class="text-sm mt-1">
              <span class="text-red-500 font-semibold">
                {{ statusSummary.absent }}
              </span>
              <span class="mx-1 text-gray-400">/</span>
              <span class="text-yellow-600 font-semibold">
                {{ statusSummary.excused }}
              </span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- MAIN CONTENT -->
      <el-row :gutter="16" class="mt-4">
        <!-- LEFT: FORM -->
        <el-col :xs="24" :lg="10">
          <el-card shadow="hover">
            <template #header>
              <span class="font-semibold">Mark attendance</span>
            </template>

            <el-form
              :model="attendanceForm"
              label-width="110px"
              size="small"
              class="mb-2"
            >
              <el-form-item label="Student">
                <el-select
                  v-model="attendanceForm.student_id"
                  placeholder="Select student"
                  :disabled="!selectedClassId || !studentOptions.length"
                  filterable
                >
                  <el-option
                    v-for="s in studentOptions"
                    :key="s.id"
                    :label="s.username"
                    :value="s.id"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="Status">
                <el-select v-model="attendanceForm.status" placeholder="Select">
                  <el-option label="Present" value="present" />
                  <el-option label="Absent" value="absent" />
                  <el-option label="Excused" value="excused" />
                </el-select>
              </el-form-item>

              <el-form-item label="Date">
                <el-date-picker
                  v-model="attendanceForm.record_date"
                  type="date"
                  value-format="YYYY-MM-DD"
                  placeholder="Pick a day"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="submitAttendance">
                  Save attendance
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- RIGHT: TABLE -->
        <el-col :xs="24" :lg="14">
          <el-card shadow="hover">
            <template #header>
              <div class="flex justify-between items-center">
                <span class="font-semibold">Attendance records</span>
                <span class="text-xs text-gray-500">
                  Showing
                  {{ filteredAttendance.length }} / {{ attendanceList.length }}
                  records
                </span>
              </div>
            </template>

            <el-table
              v-if="filteredAttendance.length"
              :data="filteredAttendance"
              size="small"
              border
              height="420"
            >
              <el-table-column
                prop="student_id"
                label="Student"
                min-width="200"
              >
                <template #default="{ row }">
                  <span>{{ row.student_name || row.student_id }}</span>
                </template>
              </el-table-column>

              <el-table-column prop="record_date" label="Date" min-width="140">
                <template #default="{ row }">
                  {{ formatDate(row.record_date as any) }}
                </template>
              </el-table-column>

              <el-table-column prop="status" label="Status" min-width="120">
                <template #default="{ row }">
                  <el-tag :type="getStatusTagType(row.status)" size="small">
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column label="Actions" min-width="220" fixed="right">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    @click="quickChangeAttendanceStatus(row.id, 'present')"
                  >
                    Present
                  </el-button>
                  <el-button
                    size="small"
                    @click="quickChangeAttendanceStatus(row.id, 'absent')"
                  >
                    Absent
                  </el-button>
                  <el-button
                    size="small"
                    @click="quickChangeAttendanceStatus(row.id, 'excused')"
                  >
                    Excused
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <div
              v-else
              class="text-sm text-gray-500 italic text-center py-4 mt-2"
            >
              No attendance records for this class
              <span v-if="attendanceForm.student_id"> / student</span>.
            </div>
          </el-card>
        </el-col>
      </el-row>
    </template>
  </div>
</template>
