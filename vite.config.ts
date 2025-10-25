import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

const preferredPort = Number.parseInt(process.env.FRONTEND_PORT ?? process.env.PORT ?? "", 10);
const serverPort = Number.isFinite(preferredPort) ? preferredPort : 5173;

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: serverPort,
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
