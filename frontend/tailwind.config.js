/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f5fa',
          100: '#e1ecf5',
          200: '#c3d9eb',
          300: '#96bedd',
          400: '#629dcb',
          500: '#235e97',
          600: '#15487a',
          700: '#0f3862', // Deep Government Navy
          800: '#0b2949',
          900: '#081c33', // Deep State Navy
          950: '#040d19',
        },
        saffron: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316', // Official Tiranga Saffron
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
        govgreen: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a', // Official India Green
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        govgold: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
        },
        civic: {
          slate: '#081c33',
          blue: '#0f3862',
          emerald: '#15803d',
          amber: '#c2410c',
          crimson: '#b91c1c',
        }
      },
    },
  },
  plugins: [],
}
