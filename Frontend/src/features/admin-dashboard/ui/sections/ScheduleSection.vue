<script setup lang="ts">
import { computed } from "vue";
import type { EChartsOption } from "echarts";

import VizCard from "../components/VizCard.vue";
import DataTableCard from "../components/DataTableCard.vue";

const props = defineProps<{
  loading: boolean;
  byWeekdayOption: EChartsOption | null;
  byTeacherOption: EChartsOption | null;
  scheduleTeacherRows: any[];
}>();

const safeScheduleTeacherRows = computed(() =>
  Array.isArray(props.scheduleTeacherRows) ? props.scheduleTeacherRows : []
);
</script>

<template>
  <el-row :gutter="16" class="mt-2">
    <el-col :xs="24" :md="12">
      <VizCard
        title="Lessons by weekday"
        :loading="loading"
        :option="byWeekdayOption"
        empty-text="No schedule data"
        :height="260"
      />
    </el-col>

    <el-col :xs="24" :md="12">
      <DataTableCard title="Teaching load by teacher" :loading="loading">
        <!-- Chart card inside the table card -->
        <VizCard
          title="Teaching load chart"
          :loading="loading"
          :option="byTeacherOption"
          empty-text="No teacher schedule data"
          :height="260"
          class="!border-0 !shadow-none"
        />

        <el-table
          :data="safeScheduleTeacherRows"
          size="small"
          style="width: 100%"
          :height="200"
          border
          class="mt-3"
        >
          <el-table-column
            prop="teacher_name"
            label="Teacher"
            min-width="160"
            show-overflow-tooltip
          />
          <el-table-column prop="lessons" label="Lessons" width="90" />
          <el-table-column prop="classes" label="Classes" width="90" />
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
