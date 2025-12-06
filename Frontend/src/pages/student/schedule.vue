<!-- ~/pages/student/schedule/index.vue -->
<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";

import { studentService } from "~/api/student";
import type { ScheduleDTO } from "~/api/types/school.dto";
import type { StudentScheduleFilterDTO } from "~/api/student/student.dto";

definePageMeta({
  layout: "student",
});

const student = studentService();

const loading = ref(false);
const errorMessage = ref<string | null>(null);
const schedule = ref<ScheduleDTO[]>([]);

const loadSchedule = async () => {
  loading.value = true;
  errorMessage.value = null;
  try {
    const params: StudentScheduleFilterDTO = {};
    const res = await student.student.getMySchedule(params);
    schedule.value = res.items ?? [];
  } catch (err: any) {
    console.error(err);
    errorMessage.value = err?.message ?? "Failed to load schedule.";
    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
};

const dayOfWeekLabel = (d: number | string) => {
  const map: Record<string, string> = {
    "1": "Mon",
    "2": "Tue",
    "3": "Wed",
    "4": "Thu",
    "5": "Fri",
    "6": "Sat",
    "7": "Sun",
  };
  return map[String(d)] ?? String(d);
};

onMounted(loadSchedule);
</script>

<template>
  <div class="p-4 space-y-4">
    <el-row justify="space-between" align="middle">
      <el-col :span="18">
        <h1 class="text-xl font-semibold">My Schedule</h1>
        <p class="text-xs text-gray-500">All your lessons and timings.</p>
      </el-col>
      <el-col :span="6" class="text-right">
        <el-button type="primary" :loading="loading" @click="loadSchedule">
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

    <el-card shadow="hover">
      <el-table
        :data="schedule"
        v-loading="loading"
        border
        size="small"
        style="width: 100%"
      >
        <el-table-column prop="day_of_week" label="Day" min-width="90">
          <template #default="{ row }">
            {{ dayOfWeekLabel(row.day_of_week) }}
          </template>
        </el-table-column>

        <el-table-column prop="start_time" label="Start" min-width="90" />
        <el-table-column prop="end_time" label="End" min-width="90" />
        <el-table-column prop="class_name" label="Class" min-width="200" />
        <el-table-column prop="teacher_name" label="Teacher" min-width="200" />
        <el-table-column prop="room" label="Room" min-width="100" />
      </el-table>

      <div
        v-if="!loading && !schedule.length"
        class="text-center text-gray-500 text-sm py-4"
      >
        No schedule data yet.
      </div>
    </el-card>
  </div>
</template>
