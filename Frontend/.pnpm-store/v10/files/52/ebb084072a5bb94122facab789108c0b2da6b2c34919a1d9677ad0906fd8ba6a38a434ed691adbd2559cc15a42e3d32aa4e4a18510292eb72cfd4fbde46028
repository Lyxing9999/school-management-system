declare module '@capsizecss/metrics/basic' {
  interface BasicMetrics {
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
  export const fontMetrics: BasicMetrics;
  export default fontMetrics;
}
