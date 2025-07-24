<template>
  <VChart :option="chartOptions" style="height: 400px; width: 100%" />
</template>

<script setup lang="ts">
const chartOptions = {
  title: {
    text: "Users by Role",
    textStyle: {
      fontSize: 18,
      fontWeight: "bold",
    },
  },
  tooltip: {
    trigger: "item",
    formatter: "{b}: {c} ({d}%)",
  },
  series: [
    {
      name: "Users",
      type: "pie",
      radius: ["40%", "70%"],
      avoidLabelOverlap: true,
      itemStyle: {
        borderRadius: 10,
        borderColor: "#fff",
        borderWidth: 2,
      },
      label: {
        show: true,
        formatter: "{b}: {c}",
      },
      data: [
        { value: 120, name: "Students" },
        { value: 45, name: "Teachers" },
        { value: 15, name: "Admins" },
      ],
    },
  ],
};
</script>

<style scoped>
/* Add any custom styles here if needed */
</style>
