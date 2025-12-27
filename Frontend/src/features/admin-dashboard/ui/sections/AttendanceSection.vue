<script setup lang="ts">
import { computed } from "vue";
import type { EChartsOption } from "echarts";
import type { TopAbsentStudentRow } from "../../model/normalize";

import VizCard from "../components/VizCard.vue";
import DataTableCard from "../components/DataTableCard.vue";

const props = defineProps<{
  loading: boolean;
  statusOption: EChartsOption | null;
  dailyTrendOption: EChartsOption | null;
  byClassOption: EChartsOption | null;
  topAbsentStudents: TopAbsentStudentRow[];
}>();

const safeTopAbsentStudents = computed(() =>
  Array.isArray(props.topAbsentStudents) ? props.topAbsentStudents : []
);
</script>

<template>
  <el-row :gutter="16" class="mt-2">
    <el-col :xs="24" :md="8">
      <VizCard
        title="Attendance status summary"
        :loading="loading"
        :option-exists="!!statusOption"
        empty-text="No attendance data"
      >
        <VChart
          v-if="statusOption"
          :option="statusOption"
          autoresize
          class="w-full h-full"
        />
      </VizCard>
    </el-col>

    <el-col :xs="24" :md="16">
      <VizCard
        title="Daily attendance trend"
        :loading="loading"
        :option-exists="!!dailyTrendOption"
        empty-text="No daily trend data"
      >
        <VChart
          v-if="dailyTrendOption"
          :option="dailyTrendOption"
          autoresize
          class="w-full h-full"
        />
      </VizCard>
    </el-col>
  </el-row>

  <el-row :gutter="16" class="mt-2">
    <el-col :xs="24" :md="12">
      <VizCard
        title="Attendance by class"
        :loading="loading"
        :option-exists="!!byClassOption"
        empty-text="No class-level attendance"
      >
        <VChart
          v-if="byClassOption"
          :option="byClassOption"
          autoresize
          class="w-full h-full"
        />
      </VizCard>
    </el-col>

    <el-col :xs="24" :md="12">
      <DataTableCard title="Top absent students" :loading="loading">
        <el-table
          :data="safeTopAbsentStudents"
          size="small"
          style="width: 100%"
          :height="260"
          border
        >
          <el-table-column
            prop="student_name"
            label="Student"
            min-width="160"
            show-overflow-tooltip
          />
          <el-table-column
            prop="class_name"
            label="Class"
            min-width="140"
            show-overflow-tooltip
          />
          <el-table-column prop="absent_count" label="Absent" width="80" />
          <el-table-column
            prop="total_records"
            label="Total records"
            width="110"
          />
          <template #empty>
            <div class="text-center text-gray-500 text-xs py-3">
              No data available.
            </div>
          </template>
        </el-table>
      </DataTableCard>
    </el-col>
  </el-row>
</template>
