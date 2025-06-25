import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/upload-aadhaar': { target: 'http://localhost:5000', changeOrigin: true },
      '/upload-selfie': { target: 'http://localhost:5000', changeOrigin: true },
      '/verify': { target: 'http://localhost:5000', changeOrigin: true }
    }
  }
});
