<!-- ~/pages/student/attendance/index.vue -->
<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { ElMessage } from "element-plus";

import { studentService } from "~/api/student";
import type { ClassSectionDTO, AttendanceDTO } from "~/api/types/school.dto";
import type { StudentAttendanceFilterDTO } from "~/api/student/dto";

definePageMeta({
  layout: "student",
});

const student = studentService();

const loadingClasses = ref(false);
const loadingAttendance = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<ClassSectionDTO[]>([]);
const selectedClassId = ref<string | null>(null);
const attendance = ref<AttendanceDTO[]>([]);

// ---------- load classes ----------

const loadClasses = async () => {
  loadingClasses.value = true;
  errorMessage.value = null;
  try {
    const res = await student.student.getMyClasses();
    classes.value = res.items ?? [];
    if (!selectedClassId.value && classes.value.length > 0) {
      selectedClassId.value = classes.value[0].id;
    }
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load classes.";
    ElMessage.error(errorMessage.value);
  } finally {
    loadingClasses.value = false;
  }
};

// ---------- load attendance for selected class ----------

const loadAttendance = async () => {
  if (!selectedClassId.value) {
    attendance.value = [];
    return;
  }

  loadingAttendance.value = true;
  errorMessage.value = null;
  try {
    const params: StudentAttendanceFilterDTO = {
      class_id: selectedClassId.value,
    };
    const res = await student.student.getMyAttendance(params);
    attendance.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load attendance records.";
    ElMessage.error(errorMessage.value);
  } finally {
    loadingAttendance.value = false;
  }
};

watch(selectedClassId, () => {
  loadAttendance();
});

onMounted(async () => {
  await loadClasses();
  await loadAttendance();
});
</script>

<template>
  <div class="p-4 space-y-4">
    <el-row justify="space-between" align="middle">
      <el-col :span="18">
        <h1 class="text-xl font-semibold">My Attendance</h1>
        <p class="text-xs text-gray-500">Check your attendance per class.</p>
      </el-col>

      <el-col :span="6" class="text-right">
        <el-button
          type="primary"
          :loading="loadingClasses || loadingAttendance"
          @click="
            () => {
              loadClasses();
              loadAttendance();
            }
          "
        >
          Refresh
        </el-button>
      </el-col>
    </el-row>

    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mb-2"
    />

    <el-card shadow="hover" class="space-y-4">
      <el-form inline label-width="90px" size="small">
        <el-form-item label="Class">
          <el-select
            v-model="selectedClassId"
            placeholder="Select class"
            style="min-width: 260px"
            :loading="loadingClasses"
          >
            <el-option
              v-for="c in classes"
              :key="c.id"
              :label="c.name"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table
        :data="attendance"
        v-loading="loadingAttendance"
        border
        size="small"
        style="width: 100%"
      >
        <el-table-column prop="date" label="Date" min-width="120" />
        <el-table-column prop="status" label="Status" min-width="120">
          <template #default="{ row }">
            <el-tag
              :type="
                row.status === 'present'
                  ? 'success'
                  : row.status === 'excused'
                  ? 'warning'
                  : 'danger'
              "
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="class_id"
          label="Class ID"
          min-width="260"
          show-overflow-tooltip
        />
      </el-table>

      <div
        v-if="!loadingAttendance && !attendance.length"
        class="text-center text-gray-500 text-sm py-4"
      >
        No attendance records for this class yet.
      </div>
    </el-card>
  </div>
</template>
