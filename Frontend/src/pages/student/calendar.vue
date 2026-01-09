<script setup lang="ts">
import { ref } from "vue";
import CambodiaCalendar from "~/components/calendar/CambodiaCalendar.vue";

definePageMeta({ layout: "default" });

const selectedYear = ref<number>(new Date().getFullYear());
const selectedType = ref<"all" | "public" | "school">("all");

// ref to call child methods
const calRef = ref<InstanceType<typeof CambodiaCalendar> | null>(null);

function handleToday() {
  calRef.value?.goToday();
}

function handleYearChange(year: number) {
  calRef.value?.setYear(year);
}

function handleTypeChange(t: "all" | "public" | "school") {
  calRef.value?.setType(t);
}
</script>

<template>
  <div class="p-4 md:p-6 space-y-6">
    <!-- Header -->
    <div
      class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between"
    >
      <div class="space-y-1">
        <h1 class="text-xl md:text-2xl font-semibold">Cambodia Calendar</h1>
        <p class="text-sm muted">
          Holidays and key dates. Use filters to focus on what matters.
        </p>
      </div>

      <!-- Controls -->
      <div class="flex flex-wrap items-center gap-2">
        <el-select
          v-model="selectedYear"
          size="default"
          class="w-[140px]"
          @change="handleYearChange"
        >
          <!-- simple range; adjust as you prefer -->
          <el-option
            v-for="y in 5"
            :key="y"
            :label="selectedYear - (y - 3)"
            :value="selectedYear - (y - 3)"
          />
        </el-select>

        <el-segmented
          v-model="selectedType"
          size="default"
          @change="handleTypeChange"
        >
          <el-segmented-item label="All" value="all" />
          <el-segmented-item label="Public" value="public" />
          <el-segmented-item label="School" value="school" />
        </el-segmented>

        <el-button type="primary" plain @click="handleToday">Today</el-button>
      </div>
    </div>

    <!-- Main content -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Calendar -->
      <el-card class="lg:col-span-9" shadow="never">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="font-semibold">Calendar</div>
            <div class="text-xs muted">Year: {{ selectedYear }}</div>
          </div>
        </template>

        <div class="min-h-[560px]">
          <CambodiaCalendar ref="calRef" />
        </div>
      </el-card>

      <!-- Side panel -->
      <el-card class="lg:col-span-3" shadow="never">
        <template #header>
          <div class="font-semibold">Legend</div>
        </template>

        <div class="space-y-4">
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <span
                class="w-2.5 h-2.5 rounded-full bg-[var(--el-color-success)]"
              />
              <span class="text-sm">Public Holiday</span>
            </div>
            <div class="flex items-center gap-2">
              <span
                class="w-2.5 h-2.5 rounded-full bg-[var(--el-color-warning)]"
              />
              <span class="text-sm">School Event</span>
            </div>
            <div class="flex items-center gap-2">
              <span
                class="w-2.5 h-2.5 rounded-full bg-[var(--el-color-info)]"
              />
              <span class="text-sm">Reminder</span>
            </div>
          </div>

          <el-divider />

          <div class="space-y-2">
            <div class="text-sm font-medium">Notes</div>
            <ul class="text-sm muted list-disc pl-4 space-y-1">
              <li>Click an event to see details.</li>
              <li>Use filters to reduce noise.</li>
              <li>“Today” jumps to the current date.</li>
            </ul>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.muted {
  color: var(--muted-color);
}
</style>
