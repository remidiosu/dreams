declare module 'd3-force-3d' {
  export function forceCollide(radius?: number): {
    radius(r: number): ReturnType<typeof forceCollide>
    strength(s: number): ReturnType<typeof forceCollide>
  }
}
