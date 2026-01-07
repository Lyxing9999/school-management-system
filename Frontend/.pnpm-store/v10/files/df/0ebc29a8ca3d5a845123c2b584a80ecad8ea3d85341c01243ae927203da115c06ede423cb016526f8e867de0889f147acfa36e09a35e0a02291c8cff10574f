declare module '@capsizecss/metrics/mate' {
  interface MateMetrics {
    familyName: string;
    fullName: string;
    postscriptName: string;
    category: string;
    capHeight: number;
    ascent: number;
    descent: number;
    lineGap: number;
    unitsPerEm: number;
    xHeight: number;
    xWidthAvg: number;
    subsets: Record<
      'latin' | 'thai',
      {
        xWidthAvg: number;
      }
    >;
  }
  export const fontMetrics: MateMetrics;
  export default fontMetrics;
}
