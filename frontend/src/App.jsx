import { BrowserRouter, Routes, Route } from 'react-router-dom'
import CustomCursor from './components/CustomCursor'
import Navbar from './components/Navbar'
import MainPage from './pages/MainPage'

function AppRoutes() {
  return (
    <>
      <CustomCursor />
      <Navbar />
      <Routes>
        <Route path="/" element={<MainPage />} />
        {/* 모든 경로 → 메인 */}
        <Route path="*" element={<MainPage />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}
