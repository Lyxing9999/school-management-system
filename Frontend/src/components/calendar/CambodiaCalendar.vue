<script setup lang="ts">
import { reportError } from "~/utils/errors/errors";
import { ref, onMounted, watch } from "vue";
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";

type FilterType = "all" | "public" | "school";

const apiKey = useRuntimeConfig().public.calendarificApiKey;

const year = ref<number>(new Date().getFullYear());
const type = ref<FilterType>("all");

const calendarRef = ref<InstanceType<typeof FullCalendar> | null>(null);

const showDialog = ref(false);
const selectedHoliday = ref<{
  title: string;
  date: string;
  description: string;
} | null>(null);

type HolidayEvent = {
  title: string;
  date: string;
  color?: string;
  extendedProps?: { description?: string; kind?: FilterType };
};

const events = ref<HolidayEvent[]>([]);

const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: "dayGridMonth",
  height: "auto",
  headerToolbar: { right: "prev,next", center: "title", left: "" },
  events: [] as any[],
  eventClick(info: any) {
    const event = info.event;
    selectedHoliday.value = {
      title: event.title,
      date: event.startStr,
      description: event.extendedProps.description || "No description",
    };
    showDialog.value = true;
  },
  eventDidMount(info: any) {
    tippy(info.el, {
      content: info.event.extendedProps.description || info.event.title,
      placement: "top",
    });
  },
});

function applyEvents() {
  const filtered =
    type.value === "all"
      ? events.value
      : events.value.filter((e) => e.extendedProps?.kind === type.value);

  calendarOptions.value.events = filtered;
}

async function fetchCambodiaHolidays(y: number) {
  try {
    const cacheKey = `cambodia_holidays_${y}`;
    const cached = import.meta.client ? localStorage.getItem(cacheKey) : null;

    if (cached) {
      events.value = JSON.parse(cached);
      applyEvents();
      return;
    }

    const res = await fetch(
      `https://calendarific.com/api/v2/holidays?api_key=${apiKey}&country=KH&year=${y}`
    );
    const data = await res.json();

    if (data?.meta?.code === 200 && data?.response?.holidays) {
      const mapped: HolidayEvent[] = data.response.holidays.map(
        (holiday: any) => ({
          title: holiday.name,
          date: holiday.date.iso,
          color: "var(--color-primary)",
          extendedProps: {
            description: holiday.description,
            // You can map to "public/school" if your API provides categories
            kind: "public",
          },
        })
      );

      if (import.meta.client)
        localStorage.setItem(cacheKey, JSON.stringify(mapped));
      events.value = mapped;
      applyEvents();
      return;
    }

    const detail = data?.meta?.error_detail ?? "Unknown API error";
    reportError(new Error(detail), "holidays.fetch.api", "log");
  } catch (error) {
    reportError(error as any, "holidays.fetch.exception", "log");
  }
}

function goToday() {
  const api = calendarRef.value?.getApi?.();
  api?.today();
}

function setYear(y: number) {
  year.value = y;
  // Optional: also navigate calendar to that year
  const api = calendarRef.value?.getApi?.();
  if (api) {
    const d = new Date(api.getDate());
    d.setFullYear(y);
    api.gotoDate(d);
  }
}

function setType(t: FilterType) {
  type.value = t;
  applyEvents();
}

defineExpose({ goToday, setYear, setType });

watch(year, async (y) => {
  await fetchCambodiaHolidays(y);
});

onMounted(async () => {
  await fetchCambodiaHolidays(year.value);
});
</script>

<template>
  <FullCalendar ref="calendarRef" :options="calendarOptions" />

  <el-dialog
    v-model="showDialog"
    :title="selectedHoliday?.title"
    width="420px"
    center
  >
    <p class="text-sm"><strong>Date:</strong> {{ selectedHoliday?.date }}</p>
    <p class="text-sm mt-2">
      <strong>Description:</strong> {{ selectedHoliday?.description }}
    </p>

    <template #footer>
      <el-button @click="showDialog = false">Close</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
/* Column header row background (the white bar) */
:deep(.fc .fc-col-header-cell) {
  background: color-mix(in srgb, var(--hover-bg) 55%, transparent) !important;
  border-color: var(--border-color) !important;
}

/* Column header text */
:deep(.fc .fc-col-header-cell-cushion) {
  color: var(--muted-color) !important;
  font-weight: 700;
  text-decoration: none !important;
  padding: 10px 0 !important;
}
</style>
