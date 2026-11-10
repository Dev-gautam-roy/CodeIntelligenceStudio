import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        root: "#0B0F17",
        surface: {
          1: "#111827",
          2: "#1F2937",
          3: "#374151",
        },
        border: {
          default: "#1E293B",
          focus: "#3B82F6",
        },
      },
    },
  },
  plugins: [],
};

export default config;
