import type { Config } from "tailwindcss";

const config: Config = {
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
  },
  // Plugins moved to CSS directive (@plugin "@tailwindcss/typography" in index.css)
  // tailwindcss-animate moved to CSS directive (@plugin "tailwindcss-animate" in index.css)
};

export default config;
