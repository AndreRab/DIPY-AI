import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

// https://vite.dev/config/
const repositoryRoot = path.resolve(import.meta.dirname, '..')

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, repositoryRoot, 'BACKEND_URL')

  return {
    envDir: repositoryRoot,
    define: {
      'import.meta.env.BACKEND_URL': JSON.stringify(
        env.BACKEND_URL ?? 'http://localhost:8000',
      ),
    },
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(import.meta.dirname, './src'),
      },
    },
  }
})
