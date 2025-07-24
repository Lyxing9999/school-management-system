<script lang="ts" setup>
import { ref, computed } from "vue";
import { useWindowSize } from "~/composables/useWindowSize";
import StatisticsOverviewView from "~/views/admin/Dashboard/StatisticsOverviewView.vue";
import CambodiaCalendar from "~/components/Calendar/CambodiaCalendar.vue";
import PieChart from "~/components/Charts/PieChart.vue";
import BarChart from "~/components/Charts/BarChart.vue";

definePageMeta({ layout: "admin" });

const XL_BREAKPOINT = 1080;
const { width } = useWindowSize();
const isXL = computed(() => width.value >= XL_BREAKPOINT);

// For tabs on small screens
const activeTab = ref("charts");
</script>

<template>
  <el-row class="p-4" :gutter="20">
    <el-col :xs="24" :xl="16">
      <template v-if="!isXL">
        <!-- Tabs on small screens -->
        <el-tabs v-model="activeTab" stretch>
          <el-tab-pane label="Charts & Stats" name="charts" :key="'charts'">
            <StatisticsOverviewView />
            <el-row :gutter="20" class="mt-4">
              <el-col :xs="24" :md="12"><PieChart /></el-col>
              <el-col :xs="24" :md="12"><BarChart /></el-col>
            </el-row>
          </el-tab-pane>
          <el-tab-pane label="Calendar" name="calendar" :key="'calendar'">
            <CambodiaCalendar />
          </el-tab-pane>
        </el-tabs>
      </template>

      <template v-else>
        <!-- Show all together on large screens -->
        <StatisticsOverviewView />
        <el-row :gutter="20" class="mt-4">
          <el-col :xs="24" :md="12"><PieChart /></el-col>
          <el-col :xs="24" :md="12"><BarChart /></el-col>
        </el-row>
      </template>
    </el-col>

    <!-- Sidebar calendar for XL and up -->
    <el-col :xl="8" v-if="isXL">
      <CambodiaCalendar />
    </el-col>
  </el-row>
</template>
