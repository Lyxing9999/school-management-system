<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useHolidays, type FilterType } from "~/composables/useHolidays";

interface CalendarEvent {
  date: string;
  title: string;
  type: "public" | "school";
  description?: string;
}

const { filteredEvents, fetchHolidays, currentFilter } = useHolidays();

const viewDate = ref(new Date());
const showDialog = ref(false);
const selectedEvent = ref<CalendarEvent | null>(null);

const MAX_EVENTS_PER_CELL = 3;

const startOfMonth = (d: Date) => new Date(d.getFullYear(), d.getMonth(), 1);
const pad2 = (n: number) => String(n).padStart(2, "0");
const toISODate = (d: Date) =>
  `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;

const calendarCells = computed(() => {
  const start = startOfMonth(viewDate.value);
  const startWeekday = start.getDay(); // Sun=0..Sat=6
  const gridStart = new Date(start);
  gridStart.setDate(start.getDate() - startWeekday);

  const cells: Array<{
    date: Date;
    iso: string;
    inMonth: boolean;
    day: number;
    isToday: boolean;
  }> = [];

  const todayISO = toISODate(new Date());
  const currentMonth = viewDate.value.getMonth();

  for (let i = 0; i < 42; i++) {
    const d = new Date(gridStart);
    d.setDate(gridStart.getDate() + i);
    const iso = toISODate(d);
    cells.push({
      date: d,
      iso,
      inMonth: d.getMonth() === currentMonth,
      day: d.getDate(),
      isToday: iso === todayISO,
    });
  }
  return cells;
});

const eventsByDate = computed(() => {
  const map = new Map<string, CalendarEvent[]>();
  for (const e of filteredEvents.value) {
    const list = map.get(e.date) ?? [];
    list.push(e);
    map.set(e.date, list);
  }
  return map;
});

// --- Smart Limiting Logic ---
const visibleEvents = (iso: string) => {
  const list = eventsByDate.value.get(iso) || [];
  return list.slice(0, MAX_EVENTS_PER_CELL);
};

const hiddenCount = (iso: string) => {
  const list = eventsByDate.value.get(iso) || [];
  return Math.max(0, list.length - MAX_EVENTS_PER_CELL);
};

const monthLabel = computed(() =>
  new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric" }).format(
    viewDate.value
  )
);

const goPrev = () => {
  const d = new Date(viewDate.value);
  d.setMonth(d.getMonth() - 1);
  viewDate.value = d;
};

const goNext = () => {
  const d = new Date(viewDate.value);
  d.setMonth(d.getMonth() + 1);
  viewDate.value = d;
};

const handleEventClick = (event: CalendarEvent) => {
  selectedEvent.value = event;
  showDialog.value = true;
};

// exposed for parent
const goToday = () => (viewDate.value = new Date());
const setYear = (y: number) => {
  const d = new Date(viewDate.value);
  d.setFullYear(y);
  viewDate.value = d;
};
const setType = (t: FilterType) => (currentFilter.value = t);

defineExpose({ goToday, setYear, setType });

watch(
  () => viewDate.value.getFullYear(),
  (newYear) => fetchHolidays(newYear),
  { immediate: true }
);
</script>

<template>
  <div class="calendar-wrapper">
    <div class="calendar-header">
      <el-button-group>
        <el-button @click="goPrev">Prev</el-button>
        <el-button @click="goNext">Next</el-button>
      </el-button-group>

      <h2 class="month-label">{{ monthLabel }}</h2>
    </div>

    <div class="calendar-grid-container">
      <div class="week-header">
        <div
          v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']"
          :key="day"
          class="week-day"
        >
          {{ day }}
        </div>
      </div>

      <div class="days-grid">
        <div
          v-for="cell in calendarCells"
          :key="cell.iso"
          class="day-cell"
          :class="{ 'out-of-month': !cell.inMonth, 'is-today': cell.isToday }"
        >
          <div class="day-header">
            <span class="day-number">{{ cell.day }}</span>
          </div>

          <div class="events-list">
            <div
              v-for="(event, idx) in visibleEvents(cell.iso)"
              :key="idx"
              @click.stop="handleEventClick(event)"
              class="event-item"
              :class="event.type"
              :title="event.title"
            >
              {{ event.title }}
            </div>

            <div v-if="hiddenCount(cell.iso) > 0" class="more-indicator">
              +{{ hiddenCount(cell.iso) }} more
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="showDialog"
      :title="selectedEvent?.title"
      width="400px"
      align-center
    >
      <div class="dialog-content">
        <div class="dialog-row">
          <span class="label">Date:</span>
          <el-tag size="small" effect="plain">{{ selectedEvent?.date }}</el-tag>
        </div>

        <div class="dialog-row">
          <span class="label">Type:</span>
          <el-tag
            size="small"
            :type="selectedEvent?.type === 'public' ? 'primary' : 'warning'"
          >
            {{ selectedEvent?.type }}
          </el-tag>
        </div>

        <div class="dialog-desc">
          <p class="label">Description:</p>
          <p class="desc-text">
            {{ selectedEvent?.description || "No description available." }}
          </p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.week-header,
.days-grid {
  min-width: 0;
}
.day-cell,
.events-list,
.event-item {
  min-width: 0;
}

.calendar-wrapper {
  /* width */
  width: 100%;
  max-width: 1280px;
  margin: 0 auto; /* center */

  background-color: var(--color-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-base);
  padding: 24px;

  box-shadow: 0 8px 22px color-mix(in srgb, var(--card-shadow) 70%, transparent),
    0 1px 0 color-mix(in srgb, var(--border-color) 55%, transparent);
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
}

.month-label {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0;
  letter-spacing: -0.02em;
}

.calendar-grid-container {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-base);
  overflow: hidden;
}

.week-header {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  background-color: var(--color-bg);
  border-bottom: 1px solid var(--border-color);
}

.week-day {
  padding: 12px 8px;
  text-align: center;
  font-size: 0.875rem;
  font-weight: 650;
  color: var(--muted-color);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  user-select: none;
}

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 1px;
  background-color: var(--border-color);
}

.day-cell {
  background-color: var(--color-card);
  height: 140px;
  min-height: 140px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: background-color var(--transition-base);
}

.day-cell:hover {
  background-color: var(--hover-bg);
}

.out-of-month {
  background-color: color-mix(
    in srgb,
    var(--color-bg) 55%,
    var(--color-card) 45%
  );
}

.day-header {
  display: flex;
  justify-content: flex-end;
}

.day-number {
  font-size: 0.875rem;
  font-weight: 650;
  color: var(--text-color);
  padding: 2px 8px;
  border-radius: 999px;
  line-height: 22px;
}

.out-of-month .day-number {
  color: color-mix(in srgb, var(--muted-color) 78%, transparent);
}

.is-today .day-number {
  background-color: var(--color-primary);
  color: var(--color-light);
  box-shadow: 0 6px 14px
    color-mix(in srgb, var(--color-primary) 30%, transparent);
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow: hidden;
  flex: 1;
}

.event-item {
  font-size: 0.75rem;
  padding: 4px 6px;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 600;
  transition: transform 0.1s ease, filter 0.1s ease;
}

.event-item:hover {
  transform: translateY(-0.5px);
  filter: brightness(0.98);
}

.event-item.public {
  background-color: var(--color-primary-light-8);
  color: var(--color-primary);
  border-left: 3px solid var(--color-primary);
}

.event-item.school {
  background-color: color-mix(
    in srgb,
    var(--button-warning-bg) 18%,
    transparent
  );
  border-left: 3px solid var(--button-warning-bg);
  color: var(--text-color); /* ✅ good in light */
}

html[data-theme="dark"] .event-item.school {
  color: var(--button-warning-bg);
}

html[data-theme="dark"] .event-item.public {
  background-color: var(--color-primary-light-6);
  color: var(--color-primary-light-2);
}

.more-indicator {
  margin-top: 2px;
  font-size: 0.75rem;
  font-weight: 650;
  color: var(--muted-color);
  padding: 2px 6px;
  border-radius: 6px;
  width: fit-content;
  background: color-mix(in srgb, var(--color-bg) 70%, transparent);
  user-select: none;
}

.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialog-desc {
  background-color: var(--color-bg);
  padding: 12px;
  border-radius: var(--border-radius-base);
  border: 1px solid var(--border-color);
}

.label {
  font-weight: 650;
  color: var(--text-color);
  font-size: 0.875rem;
}

.desc-text {
  color: var(--muted-color);
  font-size: 0.875rem;
  margin-top: 4px;
  line-height: 1.6;
}

@media (max-width: 640px) {
  .calendar-wrapper {
    padding: 14px;
  }

  .day-cell {
    height: 96px;
    min-height: 96px;
    padding: 4px;
    gap: 4px;
  }

  .week-day {
    padding: 8px 2px;
    font-size: 0.7rem;
  }

  .event-item {
    font-size: 0.65rem;
    padding: 2px 4px;
    border-radius: 6px;
  }

  .more-indicator {
    font-size: 0.68rem;
    padding: 2px 5px;
  }
}
</style>
