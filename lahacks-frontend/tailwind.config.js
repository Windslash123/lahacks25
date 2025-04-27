/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    ttheme: {
      extend: {
        fontFamily: {
          outfit: ['Outfit', 'sans-serif'],
        },
      },
    },    
    plugins: [],
  }
  