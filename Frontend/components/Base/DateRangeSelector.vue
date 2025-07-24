<script setup lang="ts">
import { ref, computed, onMounted, defineEmits } from "vue";

export type DateRangeType = "all" | "day" | "week" | "month";

export type FormattedDatesPayload = {
  previous_start_date: string;
  previous_end_date: string;
  current_start_date: string;
  current_end_date: string;
} | null;

const dateRangeType = ref<DateRangeType>("all");
const dateRange = ref<[Date, Date] | []>([]);

const emit = defineEmits<{
  (
    event: "formattedDates",
    payload: FormattedDatesPayload,
    type: DateRangeType
  ): void;
}>();

const handleRangeChange = (type: DateRangeType) => {
  const endDate = new Date();
  let startDate = new Date();

  switch (type) {
    case "all":
      startDate = new Date(2000, 0, 1);
      break;
    case "day":
      startDate.setDate(endDate.getDate() - 1);
      break;
    case "week":
      startDate.setDate(endDate.getDate() - 7);
      break;
    case "month":
      startDate.setMonth(endDate.getMonth() - 1);
      break;
  }

  dateRange.value = [startDate, endDate];

  if (formattedDates.value) {
    emit("formattedDates", formattedDates.value, type);
  }
};

const formatDate = (date: Date) => date.toISOString().split("T")[0];

const formattedDates = computed(() => {
  if (!dateRange.value || dateRange.value.length !== 2) return null;

  const [start, end] = dateRange.value;
  const rangeDays = (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);

  return {
    previous_start_date: formatDate(
      new Date(
        start.getFullYear(),
        start.getMonth(),
        start.getDate() - rangeDays
      )
    ),
    previous_end_date: formatDate(
      new Date(start.getTime() - 1000 * 60 * 60 * 24)
    ),
    current_start_date: formatDate(start),
    current_end_date: formatDate(end),
  };
});

onMounted(() => {
  handleRangeChange(dateRangeType.value);
});
</script>

<template>
  <div class="date-range-selector">
    <el-radio-group
      v-model="dateRangeType"
      style="--el-color-primary"
      @change="(e) => handleRangeChange(e as DateRangeType)"
    >
      <el-radio-button label="all">All Time</el-radio-button>
      <el-radio-button label="day">Daily</el-radio-button>
      <el-radio-button label="week">Weekly</el-radio-button>
      <el-radio-button label="month">Monthly</el-radio-button>
    </el-radio-group>
  </div>
</template>
