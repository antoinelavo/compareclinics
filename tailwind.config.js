const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', 'sans-serif'],
      },
      colors: {
        blue: {
            50:  '#EBF8FF',
            100: '#DBF1FF',
            200: '#BDE5FF',
            300: '#93D3FF',
            400: '#69C1FF',
            500: '#3D9BE9', // Your primary
            600: '#2686D1',
            700: '#1C6AA9',
            800: '#125082',
            900: '#0B365B',
        },
        accentBlue: '#3D9BE9',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography')
  ],
};
