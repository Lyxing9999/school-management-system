<template>
  <div class="calendar-container">
    <FullCalendar ref="calendarRef" :options="calendarOptions" />

    <el-dialog
      v-model="showDialog"
      :title="selectedHoliday?.title"
      width="420px"
      center
      align-center
    >
      <div class="flex flex-col gap-3">
        <div
          class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300"
        >
          <span class="font-bold">Date:</span>
          <el-tag size="small" effect="plain">{{
            selectedHoliday?.date
          }}</el-tag>
        </div>

        <div class="text-sm">
          <p class="font-bold mb-1">Description:</p>
          <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
            {{ selectedHoliday?.description || "No description available." }}
          </p>
        </div>
      </div>

      <template #footer>
        <el-button @click="showDialog = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";
// Adjust this import path based on your actual file structure
import { reportError } from "~/utils/errors/errors";

// --- Types ---
type FilterType = "all" | "public" | "school";

interface HolidayEvent {
  title: string;
  date: string; // ISO String YYYY-MM-DD
  color?: string;
  extendedProps?: {
    description?: string;
    kind?: FilterType;
  };
}

// --- Configuration ---
const config = useRuntimeConfig();
const apiKey = config.public.calendarificApiKey;

// --- State ---
const year = ref<number>(new Date().getFullYear());
const type = ref<FilterType>("all");
const calendarRef = ref<InstanceType<typeof FullCalendar> | null>(null);
const showDialog = ref(false);
const selectedHoliday = ref<{
  title: string;
  date: string;
  description: string;
} | null>(null);
const events = ref<HolidayEvent[]>([]);

// --- Calendar Options ---
const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: "dayGridMonth",
  height: "auto",
  headerToolbar: { right: "prev,next", center: "title", left: "" },
  events: [] as HolidayEvent[],

  // Handle Event Click
  eventClick(info: any) {
    const event = info.event;
    selectedHoliday.value = {
      title: event.title,
      date: event.startStr,
      description: event.extendedProps.description || "No description",
    };
    showDialog.value = true;
  },

  // Tooltip on Hover
  eventDidMount(info: any) {
    tippy(info.el, {
      content: info.event.extendedProps.description || info.event.title,
      placement: "top",
      theme: "light", // Optional: customize tippy theme
    });
  },
});

// --- Logic ---

/**
 * Filter events based on the selected type (all | public | school)
 */
function applyEvents() {
  const filtered =
    type.value === "all"
      ? events.value
      : events.value.filter((e) => e.extendedProps?.kind === type.value);

  calendarOptions.value.events = filtered;
}

/**
 * Fetch holidays from API or Cache
 * Uses $fetch for better Nuxt integration
 */
async function fetchCambodiaHolidays(y: number) {
  const cacheKey = `cambodia_holidays_${y}`;

  if (import.meta.client) {
    try {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        events.value = JSON.parse(cached);
        applyEvents();
        return; // Exit if cache hit
      }
    } catch (e) {
      console.warn("Error reading from localStorage", e);
    }
  }

  try {
    const data = await $fetch<any>("https://calendarific.com/api/v2/holidays", {
      params: {
        api_key: apiKey,
        country: "KH",
        year: y,
      },
    });

    if (data?.meta?.code === 200 && data?.response?.holidays) {
      const mapped: HolidayEvent[] = data.response.holidays.map(
        (holiday: any) => ({
          title: holiday.name,
          date: holiday.date.iso,
          color: "var(--color-primary)",
          extendedProps: {
            description: holiday.description,
            kind: "public", // Defaulting to public since API doesn't specify school
          },
        })
      );

      if (import.meta.client) {
        try {
          localStorage.setItem(cacheKey, JSON.stringify(mapped));
        } catch (e) {
          console.warn("Quota exceeded or error saving to localStorage");
        }
      }

      events.value = mapped;
      applyEvents();
    } else {
      // Handle API Logic Error (e.g., Invalid Key)
      const detail = data?.meta?.error_detail ?? "Unknown API error";
      reportError(new Error(detail), "holidays.fetch.api", "log");
    }
  } catch (error) {
    // Handle Network/Fetch Error
    reportError(error as any, "holidays.fetch.exception", "log");
  }
}

// --- Exposed Methods (via Template Refs) ---
function goToday() {
  const api = calendarRef.value?.getApi?.();
  api?.today();
}

function setYear(y: number) {
  year.value = y;
  // Sync internal calendar view
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

// --- Lifecycle ---
watch(year, async (y) => {
  await fetchCambodiaHolidays(y);
});

onMounted(async () => {
  await fetchCambodiaHolidays(year.value);
});
</script>

<style scoped>
/* Customizing FullCalendar Header */
:deep(.fc .fc-col-header-cell) {
  background: color-mix(
    in srgb,
    var(--el-color-primary-light-9) 55%,
    transparent
  ) !important;
  border-color: var(--el-border-color-light) !important;
}

:deep(.fc .fc-col-header-cell-cushion) {
  color: var(--el-text-color-regular) !important;
  font-weight: 600;
  text-decoration: none !important;
  padding: 12px 0 !important;
}

/* Event Styling */
:deep(.fc-event) {
  cursor: pointer;
  border: none;
  font-size: 0.85rem;
  padding: 2px;
}

:deep(.fc-daygrid-day-number) {
  color: var(--el-text-color-primary);
  text-decoration: none;
}
</style>
