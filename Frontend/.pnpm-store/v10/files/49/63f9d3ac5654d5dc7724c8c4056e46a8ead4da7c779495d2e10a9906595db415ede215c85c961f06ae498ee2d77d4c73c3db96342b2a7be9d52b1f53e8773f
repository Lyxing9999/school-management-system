declare module '@capsizecss/metrics/caudex' {
  interface CaudexMetrics {
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
  export const fontMetrics: CaudexMetrics;
  export default fontMetrics;
}
