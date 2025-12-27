<script setup lang="ts">
import { computed } from "vue";
import type { EChartsOption } from "echarts";
import VizCard from "../components/VizCard.vue";
import DataTableCard from "../components/DataTableCard.vue";

const props = defineProps<{
  loading: boolean;
  avgBySubjectOption: EChartsOption | null;
  distributionOption: EChartsOption | null;
  passRateOption: EChartsOption | null;
  passRateRows: any[];
}>();

const safePassRateRows = computed(() =>
  Array.isArray(props.passRateRows) ? props.passRateRows : []
);
</script>

<template>
  <el-row :gutter="16" class="mt-2">
    <el-col :xs="24" :md="12">
      <VizCard
        title="Average score by subject"
        :loading="loading"
        :option-exists="!!avgBySubjectOption"
        empty-text="No grade data"
      >
        <VChart
          v-if="avgBySubjectOption"
          :option="avgBySubjectOption"
          autoresize
          class="w-full h-full"
        />
      </VizCard>
    </el-col>

    <el-col :xs="24" :md="12">
      <VizCard
        title="Score distribution"
        :loading="loading"
        :option-exists="!!distributionOption"
        empty-text="No grade distribution"
      >
        <VChart
          v-if="distributionOption"
          :option="distributionOption"
          autoresize
          class="w-full h-full"
        />
      </VizCard>
    </el-col>
  </el-row>

  <el-row :gutter="16" class="mt-2">
    <el-col :xs="24" :md="12">
      <VizCard
        title="Pass rate by class"
        :loading="loading"
        :option-exists="!!passRateOption"
        empty-text="No pass-rate data"
      >
        <VChart
          v-if="passRateOption"
          :option="passRateOption"
          autoresize
          class="w-full h-full"
        />
      </VizCard>
    </el-col>

    <el-col :xs="24" :md="12">
      <DataTableCard title="Pass-rate details" :loading="loading">
        <el-table
          :data="safePassRateRows"
          size="small"
          style="width: 100%"
          :height="260"
          border
        >
          <el-table-column
            prop="class_name"
            label="Class"
            min-width="150"
            show-overflow-tooltip
          />
          <el-table-column prop="avg_score" label="Avg score" width="100">
            <template #default="{ row }">{{
              Number(row.avg_score ?? 0).toFixed(2)
            }}</template>
          </el-table-column>
          <el-table-column prop="pass_rate" label="Pass rate" width="100">
            <template #default="{ row }"
              >{{ (Number(row.pass_rate ?? 0) * 100).toFixed(1) }}%</template
            >
          </el-table-column>
          <el-table-column prop="passed" label="Passed" width="80" />
          <el-table-column prop="total_students" label="Total" width="80" />
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
