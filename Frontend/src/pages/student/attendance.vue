<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import { ElMessage } from "element-plus";

import { studentService } from "~/api/student";
import { formatDate } from "~/utils/formatDate";

import type {
  StudentClassListDTO,
  StudentAttendanceListDTO,
} from "~/api/student/student.dto";

definePageMeta({
  layout: "student",
});

const student = studentService();

const loadingClasses = ref(false);
const loadingAttendance = ref(false);
const errorMessage = ref<string | null>(null);

const classes = ref<StudentClassListDTO[]>([]);
const selectedClassId = ref<string | null>(null);
const attendance = ref<StudentAttendanceListDTO[]>([]);

// ---------- load classes ----------

const loadClasses = async () => {
  loadingClasses.value = true;
  errorMessage.value = null;
  try {
    const res = await student.student.getMyClasses();
    console.log(res);
    classes.value = res.items ?? [];

    // auto-select first class
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
    // path param style: /me/attendance/<class_id>
    const res = await student.student.getMyAttendance({
      class_id: selectedClassId.value,
    });
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

const current = ref(1);
const pageSize = ref(10);
const pagedData = computed(() => {
  const start = (current.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return attendance.value.slice(start, end);
});
</script>

<template>
  <div class="p-4 space-y-4">
    <!-- Header -->
    <el-row justify="space-between" align="middle">
      <el-col :span="18">
        <h1 class="text-xl font-semibold">My Attendance</h1>
        <p class="text-xs text-gray-500">
          Check your attendance for each class.
        </p>
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

    <!-- Error -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      class="mb-2"
    />

    <!-- Main Card -->
    <el-card shadow="hover" class="space-y-4">
      <!-- Filters -->
      <el-form inline label-width="80px" size="small">
        <el-form-item label="Class">
          <el-select
            v-model="selectedClassId"
            placeholder="Select class"
            style="min-width: 260px"
            :loading="loadingClasses"
            clearable
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

      <!-- Table -->
      <el-table
        :data="attendance"
        v-loading="loadingAttendance"
        border
        size="small"
        style="width: 100%"
        highlight-current-row
      >
        <!-- Date -->
        <el-table-column prop="record_date" label="Date" min-width="130">
          <template #default="{ row }">
            {{ row.record_date }}
          </template>
        </el-table-column>

        <!-- Class -->
        <el-table-column
          prop="class_name"
          label="Class"
          min-width="160"
          show-overflow-tooltip
        />

        <!-- Status -->
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

        <!-- Teacher -->
        <el-table-column
          prop="teacher_name"
          label="Marked By"
          min-width="150"
          show-overflow-tooltip
        />

        <!-- Created at (optional small info) -->
        <el-table-column
          prop="created_at"
          label="Recorded At"
          min-width="180"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- Empty state -->
      <div
        v-if="!loadingAttendance && !attendance.length"
        class="text-center text-gray-500 text-sm py-4"
      >
        No attendance records for this class yet.
      </div>
    </el-card>

    <el-pagination
      v-model:current-page="current"
      v-model:page-size="pageSize"
      :total="attendance.length"
      layout="prev, pager, next, jumper, ->, total, sizes"
      :page-sizes="[5, 10, 20, 50]"
    />
  </div>
</template>
