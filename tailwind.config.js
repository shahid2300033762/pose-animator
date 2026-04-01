/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "tertiary": "#006947",
        "tertiary-container": "#69f6b8",
        "tertiary-dim": "#005c3d",
        "on-tertiary": "#c8ffe0",
        "on-tertiary-container": "#005a3c",
        "on-tertiary-fixed": "#00452d",
        "tertiary-fixed": "#69f6b8",
        "tertiary-fixed-dim": "#58e7ab",
        "on-tertiary-fixed-variant": "#006544",
        "on-error": "#ffefef",
        "on-error-container": "#510017",
        "error-container": "#f74b6d",
        "surface-container-highest": "#d9dde0",
        "surface-container-high": "#dfe3e6",
        "surface-container-low": "#eef1f3",
        "surface-container-lowest": "#ffffff",
        "on-primary-fixed-variant": "#001a88",
        "inverse-surface": "#0b0f10",
        "on-surface": "#2c2f31",
        "on-surface-variant": "#595c5e",
        "on-background": "#2c2f31",
        "primary-fixed": "#8999ff",
        "primary-fixed-dim": "#778aff",
        "on-secondary-fixed-variant": "#5f28c8",
        "inverse-primary": "#7387ff",
        "secondary-fixed": "#dac9ff",
        "primary-dim": "#0934e0",
        "surface-bright": "#f5f7f9",
        "surface-dim": "#d0d5d8",
        "on-primary-fixed": "#000000",
        "primary": "#2444eb",
        "secondary": "#6a37d4",
        "secondary-dim": "#5e26c7",
        "secondary-container": "#dac9ff",
        "on-secondary": "#f8f0ff",
        "on-secondary-fixed": "#40009b",
        "on-secondary-container": "#5517bf",
        "secondary-fixed-dim": "#ceb9ff",
        "outline-variant": "#abadaf",
        "background": "#f5f7f9",
        "surface": "#f5f7f9",
        "surface-container": "#e5e9eb",
        "surface-variant": "#d9dde0",
        "outline": "#747779",
        "inverse-on-surface": "#9a9d9f",
        "error-dim": "#a70138",
        "on-primary": "#f3f1ff",
        "primary-container": "#8999ff",
        "error": "#b41340"
      },
      fontFamily: {
        "headline": ["Space Grotesk", "sans-serif"],
        "body": ["Manrope", "sans-serif"],
        "label": ["Manrope", "sans-serif"],
        "manrope": ["Manrope", "sans-serif"]
      },
      borderRadius: {
        "DEFAULT": "0.25rem",
        "lg": "1rem",
        "xl": "1.5rem",
        "full": "9999px"
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
      }
    },
  },
  plugins: [],
}
