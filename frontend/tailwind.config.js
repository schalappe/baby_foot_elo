/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#009432',
        },
        background: {
          light: '#f9fafb',
          dark: '#18181b',
        },
        foreground: {
          light: '#222',
          dark: '#fff',
        },
      },
    },
  },
  plugins: [],
};
