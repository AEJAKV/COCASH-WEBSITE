import { resolve } from 'path'
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        blog: resolve(__dirname, 'blog.html'),
        'early-repayment': resolve(__dirname, 'early-repayment.html'),
        faq: resolve(__dirname, 'faq.html'),
        'loan-cashback': resolve(__dirname, 'loan-cashback.html'),
        'privacy-policy': resolve(__dirname, 'privacy-policy.html'),
        'terms-of-service': resolve(__dirname, 'terms-of-service.html'),
        'coming-soon': resolve(__dirname, 'coming-soon.html'),
        'express-document-uploader': resolve(__dirname, 'express-document-uploader.html'),
      }
    }
  }
})
