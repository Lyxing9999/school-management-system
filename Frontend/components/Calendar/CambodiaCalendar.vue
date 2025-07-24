<script setup lang="ts">
import { ref, onMounted } from "vue";
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";

const apiKey = useRuntimeConfig().public.calendarificApiKey;

const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: "dayGridMonth",
  height: "auto",
  headerToolbar: {
    right: "prev,next",
    center: "title",
    left: "",
  },
  events: [],
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
    const titleEl = info.el.querySelector(".fc-event-title");
    if (titleEl) {
      const text = titleEl.textContent || "";
      titleEl.innerHTML = `<span class="slide-text">${text}</span>`;
    }

    tippy(info.el, {
      content: info.event.extendedProps.description || info.event.title,
      placement: "top",
    });
  },
});

const fetchCambodiaHolidays = async () => {
  try {
    const year = new Date().getFullYear();
    const cacheKey = `cambodia_holidays_${year}`;
    const cached = localStorage.getItem(cacheKey);

    if (cached) {
      const holidays = JSON.parse(cached);
      calendarOptions.value.events = holidays;
      return;
    }

    const res = await fetch(
      `https://calendarific.com/api/v2/holidays?api_key=${apiKey}&country=KH&year=${year}`
    );

    const data = await res.json();
    if (data.meta?.code === 200 && data.response?.holidays) {
      const events = data.response.holidays.map((holiday: any) => ({
        title: holiday.name,
        date: holiday.date.iso,
        color: "var(--color-primary)",
        extendedProps: { description: holiday.description },
      }));

      localStorage.setItem(cacheKey, JSON.stringify(events));
      calendarOptions.value.events = events;
    } else {
      console.error("API Error:", data.meta?.error_detail || "Unknown error");
    }
  } catch (error) {
    console.error("Failed to fetch holidays", error);
  }
};

onMounted(() => {
  fetchCambodiaHolidays();
});

const showDialog = ref(false);
const selectedHoliday = ref<{
  title: string;
  date: string;
  description: string;
} | null>(null);
</script>

<template>
  <FullCalendar :options="calendarOptions" />
  <el-dialog
    v-model="showDialog"
    :title="selectedHoliday?.title"
    width="400px"
    center
  >
    <template #default>
      <p><strong>Date:</strong> {{ selectedHoliday?.date }}</p>
      <p><strong>Description:</strong> {{ selectedHoliday?.description }}</p>
    </template>
    <template #footer>
      <el-button @click="showDialog = false">Close</el-button>
    </template>
  </el-dialog>
</template>
<style lang="scss" scoped></style>
