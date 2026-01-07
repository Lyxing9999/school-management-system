declare module '@capsizecss/metrics/margarine' {
  interface MargarineMetrics {
    familyName: string;
    fullName: string;
    postscriptName: string;
    category: string;
    ascent: number;
    descent: number;
    lineGap: number;
    unitsPerEm: number;
    xWidthAvg: number;
    subsets: Record<
      'latin' | 'thai',
      {
        xWidthAvg: number;
      }
    >;
  }
  export const fontMetrics: MargarineMetrics;
  export default fontMetrics;
}
