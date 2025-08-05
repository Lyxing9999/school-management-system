<template>
  <h2 class="text-xl font-bold mb-4">Today's Attendance</h2>
  <VChart :option="chartOptions" style="height: 300px; width: 100%" />
</template>

<script setup lang="ts">
import { ref } from "vue";
import VChart from "vue-echarts";
import * as echarts from "echarts"; // Import echarts to use graphic.LinearGradient

const attendanceData = {
  present: 120,
  absent: 15,
  late: 8,
  excused: 5,
};

const chartOptions = ref({
  title: {
    text: "Today's Attendance",
    left: "center",
    textStyle: { fontSize: 18, fontWeight: "600" },
  },
  tooltip: {
    trigger: "axis",
    axisPointer: { type: "shadow" },
  },
  xAxis: {
    type: "category",
    data: ["Present", "Absent", "Late", "Excused"],
    axisTick: { alignWithLabel: true },
  },
  yAxis: {
    type: "value",
    minInterval: 1,
  },
  series: [
    {
      name: "Students",
      type: "bar",
      data: [
        attendanceData.present,
        attendanceData.absent,
        attendanceData.late,
        attendanceData.excused,
      ],
      itemStyle: {
        color: (params: any) => {
          const colors = [
            "#10B981", // emerald green for present
            "#EF4444", // warm red for absent
            "#F59E0B", // amber for late
            "#3B82F6", // royal blue for excused
          ];
          return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: colors[params.dataIndex] },
            { offset: 1, color: colors[params.dataIndex] + "80" },
          ]);
        },
      },
      barWidth: "50%",
    },
  ],
});
</script>

<style scoped></style>
