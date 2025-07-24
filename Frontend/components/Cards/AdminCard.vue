<script setup lang="ts">
import { defineProps } from "vue";
import adminIconColor from "~/assets/icons/svg/admin-color.svg";

interface Props {
  count?: number;
  growth?: number;
  normalCount?: number;
}

// Destructure props if needed in script logic
const { count, growth, normalCount } = defineProps<Props>();
</script>

<template>
  <el-card class="p-4">
    <h3 class="text-lg font-semibold mb-2">Total Admins</h3>
    <div class="flex items-center gap-4">
      <img
        :src="adminIconColor"
        alt="Colored admin icon representing total admin count"
        class="w-12 h-12"
      />

      <el-statistic v-if="normalCount !== undefined" :value="normalCount" />

      <el-statistic
        v-else
        :value="count"
        :value-style="{
          color: (growth ?? 0) >= 0 ? '#3f8600' : '#cf1322',
        }"
      >
        <template #suffix>
          <el-tag
            :type="(growth ?? 0) >= 0 ? 'success' : 'danger'"
            size="default"
          >
            {{ ((growth ?? 0) >= 0 ? "+" : "") + (growth ?? 0) }}%
          </el-tag>
        </template>
      </el-statistic>
    </div>
  </el-card>
</template>
