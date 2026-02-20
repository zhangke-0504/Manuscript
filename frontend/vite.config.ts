import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Use relative asset paths so electron file:// can load built assets correctly
  // This sets base to './' for production builds.
  const isProd = mode === 'production'
  return {
    base: isProd ? './' : '/',
    plugins: [vue()],
  }
})
