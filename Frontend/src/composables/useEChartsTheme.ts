import { ref, computed, onMounted, onBeforeUnmount } from "vue";

type AnyObj = Record<string, any>;

const deepMerge = (a: AnyObj, b: AnyObj): AnyObj => {
  const out: AnyObj = { ...a };
  for (const k of Object.keys(b)) {
    const bv = b[k];
    const av = out[k];

    if (Array.isArray(bv)) {
      out[k] = bv.slice();
      continue;
    }

    if (
      bv &&
      typeof bv === "object" &&
      av &&
      typeof av === "object" &&
      !Array.isArray(av)
    ) {
      out[k] = deepMerge(av, bv);
      continue;
    }

    out[k] = bv;
  }
  return out;
};

const cssVar = (name: string, fallback = ""): string => {
  if (typeof window === "undefined") return fallback;
  const v = getComputedStyle(document.documentElement)
    .getPropertyValue(name)
    .trim();
  return v || fallback;
};

const getThemeMode = (): "light" | "dark" => {
  if (typeof window === "undefined") return "light";
  return (
    (document.documentElement.dataset.theme as "light" | "dark") || "light"
  );
};

export const useEChartsTheme = () => {
  const themeKey = ref(0);
  let obs: MutationObserver | null = null;

  const tokens = computed(() => {
    void themeKey.value;
    const mode = getThemeMode();

    return {
      mode,
      fontFamily: cssVar("--font-family-base", "Poppins, sans-serif"),

      bg: cssVar("--color-bg", "#f6f7fb"),
      card: cssVar("--color-card", "#ffffff"),

      text: cssVar("--text-color", "#111827"),
      muted: cssVar("--muted-color", "#6b7280"),
      border: cssVar("--border-color", "#e5e7eb"),

      chart: {
        palette: [
          cssVar("--chart-1", cssVar("--color-primary", "#6b3fa0")),
          cssVar("--chart-2", "#10b981"),
          cssVar("--chart-3", "#f59e0b"),
          cssVar("--chart-4", "#06b6d4"),
          cssVar("--chart-5", "#ef4444"),
          cssVar("--chart-6", "#3b82f6"),
          cssVar("--chart-7", "#a855f7"),
          cssVar("--chart-8", "#64748b"),
        ],
        present: cssVar("--chart-present", "#22c55e"),
        absent: cssVar("--chart-absent", "#ef4444"),
        excused: cssVar("--chart-excused", "#f59e0b"),
        grid: cssVar(
          "--chart-grid",
          mode === "dark"
            ? "rgba(255,255,255,0.10)"
            : cssVar("--border-color", "#e5e7eb")
        ),
        area: cssVar(
          "--chart-area",
          mode === "dark" ? "rgba(167,139,250,0.12)" : "rgba(107,63,160,0.08)"
        ),
      },

      hoverBg: cssVar("--hover-bg", "rgba(107,63,160,0.06)"),
      activeBg: cssVar("--active-bg", "rgba(107,63,160,0.10)"),
    };
  });

  const seriesColorMap = computed(() => {
    const c = tokens.value.chart;
    return {
      Present: c.present,
      Absent: c.absent,
      Excused: c.excused,
      present: c.present,
      absent: c.absent,
      excused: c.excused,
    } as Record<string, string>;
  });

  const baseOption = computed(() => {
    const t = tokens.value;
    return {
      color: t.chart.palette,
      backgroundColor: "transparent",

      textStyle: { color: t.text, fontFamily: t.fontFamily },

      legend: {
        icon: "circle",
        itemWidth: 10,
        itemHeight: 10,
        textStyle: { color: t.muted },
      },

      tooltip: {
        backgroundColor: t.card,
        borderColor: t.border,
        borderWidth: 1,
        textStyle: { color: t.text },
        extraCssText: "border-radius:12px; padding:10px 12px;",
        axisPointer: {
          type: "line",
          lineStyle: { color: t.muted, width: 1, type: "dashed" },
        },
      },

      grid: { top: 44, left: 44, right: 18, bottom: 44, containLabel: true },

      xAxis: {
        axisLine: { lineStyle: { color: t.border } },
        axisTick: { show: false },
        axisLabel: { color: t.muted },
        splitLine: { show: false },
      },

      yAxis: {
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: t.muted },
        splitLine: { show: true, lineStyle: { color: t.chart.grid } },
      },

      animationDuration: 300,
    };
  });

  const withTheme = (option: AnyObj) => deepMerge(baseOption.value, option);

  const helpers = computed(() => {
    const t = tokens.value;
    const map = seriesColorMap.value;

    const pal = (i: number) => {
      const arr = t.chart.palette;
      return arr[((i % arr.length) + arr.length) % arr.length];
    };

    const line = (name: string, extra?: AnyObj) => {
      const color = map[name] || undefined;
      return deepMerge(
        {
          name,
          type: "line",
          smooth: true,
          symbol: "circle",
          symbolSize: 6,
          lineStyle: { width: 3, ...(color ? { color } : {}) },
          itemStyle: color ? { color } : {},
          emphasis: { focus: "series" },
        },
        extra || {}
      );
    };

    const bar = (name: string, extra?: AnyObj) => {
      const color = map[name] || undefined;
      return deepMerge(
        {
          name,
          type: "bar",
          barWidth: "60%",
          itemStyle: {
            borderRadius: [10, 10, 0, 0],
            ...(color ? { color } : {}),
          },
          emphasis: { focus: "series" },
        },
        extra || {}
      );
    };

    const areaLine = (name: string, extra?: AnyObj) => {
      const color = map[name] || undefined;
      return deepMerge(
        {
          name,
          type: "line",
          smooth: true,
          symbol: "circle",
          symbolSize: 6,
          lineStyle: { width: 3, ...(color ? { color } : {}) },
          itemStyle: color ? { color } : {},
          areaStyle: { opacity: 1, color: t.chart.area },
          emphasis: { focus: "series" },
        },
        extra || {}
      );
    };

    const pieDefaults = {
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: "transparent",
        borderWidth: 2,
      },
    };

    return { pal, seriesColorMap: map, line, bar, areaLine, pieDefaults };
  });

  onMounted(() => {
    if (typeof window === "undefined") return;

    obs = new MutationObserver(() => {
      themeKey.value += 1;
    });

    obs.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
  });

  onBeforeUnmount(() => obs?.disconnect());

  return { themeKey, tokens, baseOption, withTheme, helpers };
};
