import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const location = useLocation()
  const [dropdownOpen, setDropdownOpen] = useState(false)

  const isActive = (path) => location.pathname === path ? 'active' : ''

  const toggleDropdown = (e) => {
    e.preventDefault()
    setDropdownOpen(prev => !prev)
  }

  // 외부 클릭 시 드롭다운 닫기
  const closeDropdown = () => setDropdownOpen(false)

  return (
    <nav onClick={(e) => {
      if (!e.target.closest('.dropdown')) closeDropdown()
    }}>
      <Link to="/" className="logo">ALL IN ONE</Link>

      <div className="menu">
        <Link to="/" className={isActive('/')}>홈</Link>

        <div className={`dropdown ${dropdownOpen ? 'open' : ''}`} id="board-dropdown">
          <a href="#" className="dropdown-toggle" onClick={toggleDropdown}>
            게시판 <span className="arrow">▼</span>
          </a>
          <div className="dropdown-menu">
            <a href="#"><span className="cat-icon">📚</span>CUVIC</a>
            <a href="#"><span className="cat-icon">⚽</span>EMSYS</a>
            <a href="#"><span className="cat-icon">🎨</span>TUX</a>
            <a href="#"><span className="cat-icon">🤝</span>NestNet</a>
            <a href="#"><span className="cat-icon">🎭</span>Nova</a>
            <a href="#"><span className="cat-icon">🎵</span>PDA</a>
            <a href="#"><span className="cat-icon">💻</span>G.dev</a>
            <div className="dropdown-divider" />
            <a href="#"><span className="cat-icon">📋</span>전체 게시판</a>
          </div>
        </div>
      </div>
    </nav>
  )
}
