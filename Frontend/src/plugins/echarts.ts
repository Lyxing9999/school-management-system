import { defineNuxtPlugin } from "#app";

export default defineNuxtPlugin(async (nuxtApp) => {
  // Extra safety (client-only file already, but this prevents edge cases)
  if (import.meta.server) return;

  // Import ONLY on client
  const [{ use }, { CanvasRenderer }, charts, components, VueECharts] =
    await Promise.all([
      import("echarts/core"),
      import("echarts/renderers"),
      import("echarts/charts"),
      import("echarts/components"),
      import("vue-echarts"),
    ] as const);

  const { BarChart, LineChart, PieChart } = charts;
  const { GridComponent, TooltipComponent, LegendComponent, TitleComponent } =
    components;

  use([
    CanvasRenderer,
    BarChart,
    LineChart,
    PieChart,
    GridComponent,
    TooltipComponent,
    LegendComponent,
    TitleComponent,
  ]);

  nuxtApp.vueApp.component("VChart", VueECharts.default);
});
