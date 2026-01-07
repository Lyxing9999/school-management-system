declare module '@capsizecss/metrics/mina' {
  interface MinaMetrics {
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
  export const fontMetrics: MinaMetrics;
  export default fontMetrics;
}
