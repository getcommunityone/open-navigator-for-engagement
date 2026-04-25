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
          50: '#e8eaeb',
          100: '#c5cace',
          500: '#354F52',
          600: '#2e4346',
          700: '#27383a',
        },
        sky: {
          50: '#e8eaeb',
          100: '#c5cace',
          500: '#354F52',
          600: '#2e4346',
          700: '#27383a',
        },
        neutral: {
          600: '#354F52',
          700: '#2e4346',
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
