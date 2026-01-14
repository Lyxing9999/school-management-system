import { ref, computed } from "vue";

export type FilterType = "all" | "public" | "school";

type CalendarEvent = {
  title: string;
  date: string;
  type: "public" | "school";
  description?: string;
};

const MOCK_KH_HOLIDAYS = (year: number): CalendarEvent[] => [
  {
    title: "New Year's Day",
    date: `${year}-01-01`,
    type: "public",
    description: "International New Year",
  },
  {
    title: "Victory over Genocide",
    date: `${year}-01-07`,
    type: "public",
    description: "Commemoration day",
  },
  {
    title: "Khmer New Year",
    date: `${year}-04-14`,
    type: "public",
    description: "Traditional Cambodian New Year",
  },
  {
    title: "Khmer New Year Day 2",
    date: `${year}-04-15`,
    type: "public",
    description: "Traditional Cambodian New Year",
  },
  {
    title: "Khmer New Year Day 3",
    date: `${year}-04-16`,
    type: "public",
    description: "Traditional Cambodian New Year",
  },
  {
    title: "Visak Bochea",
    date: `${year}-05-12`,
    type: "public",
    description: "Buddha Day",
  },
  {
    title: "King's Birthday",
    date: `${year}-05-14`,
    type: "public",
    description: "Birthday of the King",
  },
  {
    title: "Pchum Ben",
    date: `${year}-09-22`,
    type: "public",
    description: "Ancestors' Day",
  },
  {
    title: "Independence Day",
    date: `${year}-11-09`,
    type: "public",
    description: "Independence from France",
  },
  {
    title: "Water Festival",
    date: `${year}-11-24`,
    type: "public",
    description: "Bonn Om Touk",
  },
];

export const useHolidays = () => {
  const allEvents = ref<CalendarEvent[]>([]);
  const currentFilter = ref<FilterType>("all");
  const isLoading = ref(false);

  const filteredEvents = computed(() => {
    if (currentFilter.value === "all") return allEvents.value;
    return allEvents.value.filter((e) => e.type === currentFilter.value);
  });

  const fetchHolidays = async (year: number) => {
    isLoading.value = true;

    try {
      const res = await $fetch<{
        meta: { ok: boolean; country: string; year: number };
        holidays: CalendarEvent[];
      }>("/api/holidays", {
        query: { country: "KH", year },
        timeout: 12000,
      });

      if (res?.holidays?.length) {
        allEvents.value = res.holidays;
      } else {
        throw new Error("Empty holidays from server");
      }
    } catch (error) {
      console.warn("Calendarific failed. Using fallback data.", error);
      allEvents.value = MOCK_KH_HOLIDAYS(year);
    } finally {
      isLoading.value = false;
    }
  };

  return { filteredEvents, currentFilter, isLoading, fetchHolidays };
};
