declare module '@capsizecss/metrics/siemreap' {
  interface SiemreapMetrics {
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
  export const fontMetrics: SiemreapMetrics;
  export default fontMetrics;
}
