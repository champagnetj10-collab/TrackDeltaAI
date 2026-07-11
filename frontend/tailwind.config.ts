import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // TrackDelta brand — single ramp so every existing `delta-*` utility
        // across the app re-themes correctly: 950/900/800 are the Carbon
        // Black / Graphite dark surfaces, 600 is the exact brand Delta Blue
        // (#0D6EFD), 400/500 are lighter accent stops for hover/secondary use.
        delta: {
          50: '#eef5ff',
          100: '#dbe9ff',
          200: '#b8d4fe',
          300: '#8ab8fc',
          400: '#5b96fa',
          500: '#2b74f5',
          600: '#0D6EFD', // brand: Delta Blue
          700: '#0a56c4',
          800: '#14213a',
          900: '#0d1620',
          950: '#0B0D10', // brand: Carbon Black
        },
        // Secondary brand accent — used sparingly (badges, highlights, warm CTAs)
        apex: {
          400: '#ff9c52',
          500: '#FF6800', // brand: Apex Orange
          600: '#e05a00',
        },
        // Exact brand neutrals, for when the delta ramp's blue tint isn't wanted
        carbon: '#0B0D10',
        graphite: '#111317',
        steel: '#E5E7EB',
      },
      fontFamily: {
        sans: ['var(--font-space-grotesk)', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'delta-gradient': 'linear-gradient(135deg, #0a1a33 0%, #0D6EFD 100%)',
        'telemetry-gradient': 'linear-gradient(135deg, #0D6EFD 0%, #7C3AED 100%)',
        'telemetry-gradient-soft': 'linear-gradient(135deg, rgba(13,110,253,0.15) 0%, rgba(124,58,237,0.15) 100%)',
        shimmer: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent)',
      },
      keyframes: {
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'slide-up': {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          from: { opacity: '0', transform: 'scale(0.97)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          from: { backgroundPosition: '-200% 0' },
          to: { backgroundPosition: '200% 0' },
        },
        'draw-line': {
          from: { strokeDashoffset: '1000' },
          to: { strokeDashoffset: '0' },
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fade-in 0.4s ease-out both',
        'slide-up': 'slide-up 0.45s cubic-bezier(0.16, 1, 0.3, 1) both',
        'scale-in': 'scale-in 0.3s cubic-bezier(0.16, 1, 0.3, 1) both',
        shimmer: 'shimmer 2s linear infinite',
        'draw-line': 'draw-line 1.8s ease-out forwards',
      },
    },
  },
  plugins: [],
  // Enable dark mode via class
  darkMode: 'class',
}

export default config
