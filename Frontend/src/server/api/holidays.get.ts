type CalendarificHoliday = {
  name: string;
  description?: string;
  date: { iso: string };
  primary_type?: string;
};

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export default defineEventHandler(async (event) => {
  const q = getQuery(event);

  const country = String(q.country ?? "KH").toUpperCase();
  const year = Number(q.year ?? new Date().getFullYear());

  if (!Number.isFinite(year) || year < 1900 || year > 2100) {
    throw createError({ statusCode: 400, statusMessage: "Invalid year" });
  }

  const config = useRuntimeConfig(event);
  const apiKey = config.calendarificApiKey; // private runtimeConfig

  if (!apiKey) {
    throw createError({
      statusCode: 500,
      statusMessage: "Missing CALENDARIFIC_API_KEY in server config",
    });
  }

  const url = "https://calendarific.com/api/v2/holidays";

  const attempts = 3;
  let lastErr: any = null;

  for (let i = 0; i < attempts; i++) {
    try {
      const data = await $fetch<any>(url, {
        query: { api_key: apiKey, country, year },
        headers: { Accept: "application/json" },
        timeout: 10000,
      });

      const holidays: CalendarificHoliday[] = data?.response?.holidays ?? [];

      return {
        meta: { ok: true, country, year },
        holidays: holidays.map((h) => ({
          title: h.name,
          date: h.date?.iso,
          type: "public" as const,
          description: h.description ?? "",
          raw_type: h.primary_type ?? "",
        })),
      };
    } catch (err: any) {
      lastErr = err;
      const status = err?.statusCode || err?.response?.status;

      // Don't retry on 4xx
      if (status && status < 500) break;

      await sleep(250 * (i + 1));
    }
  }

  throw createError({
    statusCode: 502,
    statusMessage: "Calendarific upstream error",
    data: { message: String(lastErr?.message ?? lastErr) },
  });
});
