import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: path.resolve(__dirname, 'src/ui/main.tsx'),
      output: {
        entryFileNames: 'js/embed.js',
        chunkFileNames: 'js/[name].[hash].js',
        assetFileNames: ({name}) => {
          if (/\.css$/.test(name ?? '')) {
            return 'css/style.css'
          }
          return 'assets/[name].[hash][extname]'
        }
      }
    }
  }
})