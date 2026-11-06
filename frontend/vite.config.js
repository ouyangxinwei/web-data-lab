import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// GitHub Pages serves this project from /web-data-lab/ rather than the domain root.
export default defineConfig({ plugins: [react()], base: '/web-data-lab/' });