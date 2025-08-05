<template>
  <el-card class="p-4">
    <h3 class="text-lg font-semibold mb-2">Total Teachers</h3>
    <div class="flex items-center gap-4">
      <img :src="teacherIconColor" alt="Teacher Icon" class="w-12 h-12" />

      <!-- Show normalCount if provided -->
      <el-statistic v-if="normalCount !== undefined" :value="normalCount" />

      <!-- Otherwise show count with growth and color -->
      <el-statistic
        v-else
        :value="count"
        :value-style="{ color: growth >= 0 ? '#3f8600' : '#cf1322' }">
        <template #suffix>
          <el-tag :type="growth >= 0 ? 'success' : 'danger'" size="medium">
            {{ growth >= 0 ? "+" : "" }}{{ growth }}%
          </el-tag>
        </template>
      </el-statistic>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { defineProps } from "vue";
import teacherIconColor from "~/assets/icons/svg/teacher-color.svg";

const props = defineProps<{
  normalCount?: number;
  count?: number;
  growth?: number;
}>();
</script>
