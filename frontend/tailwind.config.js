/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6fbf8',
          100: '#b3f2e8',
          500: '#34D4BF',
          600: '#2AB89F',
          700: '#239C85',
        },
        sky: {
          50: '#e6fbf8',
          100: '#b3f2e8',
          500: '#34D4BF',
          600: '#2AB89F',
          700: '#239C85',
        },
        neutral: {
          600: '#1E293B',
          700: '#0f172a',
        },
        slate: {
          500: '#64748B',
          600: '#475569',
          700: '#334155',
        },
      },
    },
  },
  plugins: [],
}
