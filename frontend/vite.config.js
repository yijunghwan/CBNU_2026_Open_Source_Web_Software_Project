import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    // npm run build 결과물이 Flask의 static/react_build/ 에 바로 생성됨
    outDir: '../static/react_build',
    emptyOutDir: true,
  },
  server: {
    // 개발 서버(npm run dev) 실행 시 API 요청을 Flask로 프록시
    proxy: {
      '/auth': 'http://localhost:5001',
      '/user': 'http://localhost:5001',
      '/club': 'http://localhost:5001',
      '/static': 'http://localhost:5001',
    }
  }
})
