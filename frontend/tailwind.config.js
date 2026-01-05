/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#8b5cf6',    // Royal Purple
        secondary: '#7c3aed',  // Dark Purple
        accent: '#a78bfa',     // Light Purple
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        'gray-50': '#faf5ff',  // Purple-tinted gray
        'gray-900': '#1e1b4b', // Deep purple-black
        sentiment: {
          positive: '#10b981', // Success green
          neutral: '#a78bfa',  // Light purple
          negative: '#ef4444', // Error red
        },
      },
      fontFamily: {
        serif: ['Playfair Display', 'Noto Serif KR', 'Georgia', 'serif'],
      },
      boxShadow: {
        'sharp': '0 2px 4px rgba(0, 0, 0, 0.15)',
      },
    },
    screens: {
      '2xl': {'max': '1535px'},
      'xl': {'max': '1279px'},
      'lg': {'max': '1023px'},
      'md': {'max': '767px'},
      'sm': {'max': '639px'},
    },
  },
  plugins: [],
}

