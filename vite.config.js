import { resolve } from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        blog: resolve(__dirname, 'blog.html'),
        faq: resolve(__dirname, 'faq.html'),
        'privacy-policy': resolve(__dirname, 'privacy-policy.html'),
        'terms-of-service': resolve(__dirname, 'terms-of-service.html'),
        'coming-soon': resolve(__dirname, 'coming-soon.html'),
      }
    }
  }
})
