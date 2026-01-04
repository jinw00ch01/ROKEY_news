/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        sentiment: {
          positive: '#16a34a',
          neutral: '#64748b',
          negative: '#dc2626',
        },
      },
    },
  },
  plugins: [],
}

