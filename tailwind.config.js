/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./**/*.html"],
  theme: {
    extend: {
      colors: {
        surface: "#FAF7F2",
        ink: "#1A1A18",
        accent: "#C4622D",
        muted: "#8A8880",
        warm: {
          50: "#FAF7F2",
          100: "#F5EFE6",
          200: "#E8E4DC",
          300: "#D4CFC5",
          400: "#B8B3A8",
          500: "#8A8880",
          600: "#5C5A54",
          700: "#3A3835",
          800: "#2A2825",
          900: "#1A1A18",
        },
      },
      fontFamily: {
        display: ["Playfair Display", "Georgia", "serif"],
        sans: ["DM Sans", "system-ui", "sans-serif"],
      },
      letterSpacing: {
        editorial: "0.2em",
        "editorial-sm": "0.14em",
        "editorial-xs": "0.12em",
      },
      boxShadow: {
        card: "0 4px 24px rgba(26, 26, 24, 0.06)",
        "card-hover": "0 8px 40px rgba(26, 26, 24, 0.1)",
      },
    },
  },
  plugins: [],
};
