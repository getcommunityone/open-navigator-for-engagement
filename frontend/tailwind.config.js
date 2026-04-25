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
          50: '#eef0f9',
          100: '#dde1f3',
          500: '#3b4db8',
          600: '#26348F',
          700: '#1e2871',
        },
        sky: {
          50: '#eef0f9',
          100: '#dde1f3',
          500: '#3b4db8',
          600: '#26348F',
          700: '#1e2871',
        },
        dark: {
          600: '#28343D',
          700: '#1f282f',
        },
      },
    },
  },
  plugins: [],
}
