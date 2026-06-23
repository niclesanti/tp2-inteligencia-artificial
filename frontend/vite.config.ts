import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import svgr from 'vite-plugin-svgr'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// Usar nombres de servicios Docker para entorno containerizado,
// con fallback a localhost para desarrollo local fuera de Docker
const AGENTE_URL = process.env.AGENTE_URL || 'http://localhost:8000'
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    svgr()
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    host: true, // Necesario para Docker
    watch: {
      usePolling: true, // Necesario para hot-reload en Docker
    },
    proxy: {
      // API Gateway: rutear /api/agente al microservicio Python
      '/api/agente': {
        target: AGENTE_URL,
        changeOrigin: true,
      },
      // Rutear el resto de /api al backend Spring Boot
      '/api': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
    },
  },
  build: {
    // Optimización para PWA
    manifest: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-select'],
        },
      },
    },
  },
})
