import { useEffect, useRef, useState } from 'react'

export default function MainPage() {
  const canvasRef = useRef(null)
  const boardSectionRef = useRef(null)
  const [boardVisible, setBoardVisible] = useState(false)

  useEffect(() => {
    // Three.js는 index.html의 CDN으로 로드됨 (window.THREE)
    if (!window.THREE) return
    const THREE = window.THREE
    const container = canvasRef.current

    // ── 씬 / 카메라 / 렌더러 ──────────────────────────────
    const scene = new THREE.Scene()
    scene.fog = new THREE.FogExp2(0x050505, 0.04)

    const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000)
    camera.position.z = 18
    camera.position.y = 2

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(container.clientWidth, container.clientHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    container.appendChild(renderer.domElement)

    // ── 파티클 ──────────────────────────────────────────
    const particlesGeo = new THREE.BufferGeometry()
    const posArray = new Float32Array(1000 * 3)
    for (let i = 0; i < posArray.length; i++) posArray[i] = (Math.random() - 0.5) * 60
    particlesGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3))
    const particlesMesh = new THREE.Points(particlesGeo, new THREE.PointsMaterial({
      size: 0.08, color: 0x00d4ff, transparent: true, opacity: 0.8,
      blending: THREE.AdditiveBlending
    }))
    scene.add(particlesMesh)

    // ── 배너 캐러셀 ──────────────────────────────────────
    const carouselGroup = new THREE.Group()
    scene.add(carouselGroup)

    const bannerCount = 8
    const radius = 13
    const bannerImages = [
      '/static/mainPage_/banner_image/CUVIC.png',
      '/static/mainPage_/banner_image/EMSYS.png',
      '/static/mainPage_/banner_image/G.DEV.FC.png',
      '/static/mainPage_/banner_image/NEST.NET.png',
      '/static/mainPage_/banner_image/NOVA.png',
      '/static/mainPage_/banner_image/pda.png',
      '/static/mainPage_/banner_image/SAMMaru.png',
      '/static/mainPage_/banner_image/TUX.png',
    ]
    const bannerURLs = [
      '/board/cuvic', '/board/emsys', '/board/gdev', '/board/nestnet',
      '/board/nova', '/board/pda', '/board/sammaru', '/board/tux',
    ]

    const textureLoader = new THREE.TextureLoader()
    for (let i = 0; i < bannerCount; i++) {
      const angle = (i / bannerCount) * Math.PI * 2
      const geometry = new THREE.BoxGeometry(4.5, 7, 0.1)
      const texture = textureLoader.load(bannerImages[i])
      const material = new THREE.MeshBasicMaterial({ map: texture, transparent: true, opacity: 0.9 })
      const mesh = new THREE.Mesh(geometry, material)

      const edges = new THREE.EdgesGeometry(geometry)
      const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({
        color: new THREE.Color().setHSL(i / bannerCount, 1, 0.6), linewidth: 2
      }))
      mesh.add(line)

      mesh.position.x = Math.cos(angle) * radius
      mesh.position.z = Math.sin(angle) * radius
      mesh.position.y = Math.sin(angle * 3) * 1.5
      mesh.rotation.y = -angle + Math.PI / 2
      mesh.userData.url = bannerURLs[i]
      carouselGroup.add(mesh)
    }

    // ── 드래그 & 클릭 ───────────────────────────────────
    let isDragging = false, prevX = 0, prevY = 0
    let targetRotY = 0, targetRotX = 0
    let mouseDownPos = { x: 0, y: 0 }
    const AUTO_SPEED = 0.002

    const onDown = (e) => {
      isDragging = true
      prevX = e.clientX ?? e.touches[0].clientX
      prevY = e.clientY ?? e.touches[0].clientY
      mouseDownPos = { x: prevX, y: prevY }
    }
    const onMove = (e) => {
      if (!isDragging) return
      const cx = e.clientX ?? e.touches[0].clientX
      const cy = e.clientY ?? e.touches[0].clientY
      targetRotY += (cx - prevX) * 0.005
      targetRotX = Math.max(-0.2, Math.min(0.2, targetRotX + (cy - prevY) * 0.002))
      prevX = cx; prevY = cy
    }
    const onUp = () => { isDragging = false; targetRotX = 0 }

    const raycaster = new THREE.Raycaster()
    const mouse = new THREE.Vector2()
    const onClick = (e) => {
      const dx = e.clientX - mouseDownPos.x, dy = e.clientY - mouseDownPos.y
      if (Math.sqrt(dx * dx + dy * dy) > 5) return
      const rect = container.getBoundingClientRect()
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
      raycaster.setFromCamera(mouse, camera)
      const hits = raycaster.intersectObjects(carouselGroup.children, true)
      if (hits.length > 0) {
        let t = hits[0].object
        while (t.parent && t.parent !== carouselGroup) t = t.parent
        if (t.userData.url) window.location.href = t.userData.url
      }
    }

    container.addEventListener('mousedown', onDown)
    container.addEventListener('click', onClick)
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
    container.addEventListener('touchstart', onDown)
    window.addEventListener('touchmove', onMove)
    window.addEventListener('touchend', onUp)

    const onResize = () => {
      camera.aspect = container.clientWidth / container.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(container.clientWidth, container.clientHeight)
    }
    window.addEventListener('resize', onResize)

    // ── 애니메이션 루프 ───────────────────────────────────
    const clock = new THREE.Clock()
    let animId
    const animate = () => {
      animId = requestAnimationFrame(animate)
      const t = clock.getElapsedTime()
      if (!isDragging) targetRotY += AUTO_SPEED
      carouselGroup.rotation.y += (targetRotY - carouselGroup.rotation.y) * 0.1
      carouselGroup.rotation.x += (targetRotX - carouselGroup.rotation.x) * 0.1
      particlesMesh.rotation.y = t * 0.05
      particlesMesh.position.y = Math.sin(t * 0.5) * 2
      carouselGroup.children.forEach((b, i) => { b.position.y = Math.sin(t * 2 + i) * 0.5 })
      renderer.render(scene, camera)
    }
    animate()

    // ── 클린업 ──────────────────────────────────────────
    return () => {
      cancelAnimationFrame(animId)
      renderer.dispose()
      if (container.contains(renderer.domElement)) container.removeChild(renderer.domElement)
      container.removeEventListener('mousedown', onDown)
      container.removeEventListener('click', onClick)
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
      window.removeEventListener('resize', onResize)
    }
  }, [])

  // ── 게시판 스크롤 진입 애니메이션 ──────────────────────────────────
  useEffect(() => {
    const section = boardSectionRef.current
    if (!section) return
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setBoardVisible(true)   // React state로 제어 → re-render 안전
          observer.disconnect()
        }
      },
      { threshold: 0.15 }
    )
    observer.observe(section)
    return () => observer.disconnect()
  }, [])

  return (
    <>
      <div id="hero-section" style={heroStyle}>
        <div id="ui-container" style={uiStyle}>
          <h1 style={titleStyle}>동아리 통합 게시판</h1>
          <p style={subtitleStyle}>화면을 드래그하여 동아리를 탐색해보세요</p>
        </div>
        <div id="canvas-container" ref={canvasRef} style={canvasStyle} />
      </div>

      {/* 게시판 섹션 */}
      <div
        id="board-section"
        ref={boardSectionRef}
        className={boardVisible ? 'is-visible' : ''}
        style={boardSectionStyle}
      >

        {/*아래 데이터를 api 데이터로 교체해야함*/}
        <BoardCard title="공용게시판" items={[
          { text: '[공지] 이번 주 동아리 연합 회의 일정', date: '10.24' },
          { text: '동아리방 대관 신청 관련 안내', date: '10.23' },
          { text: '분실물 보관소 운영 시간 변경', date: '10.21' },
          { text: '자유게시판 이용 수칙 안내', date: '10.20' },
          { text: '동아리 지원금 정산서류 양식', date: '10.19' },
        ]} />

        <BoardCard title="홍보게시판" items={[
          { text: '[밴드동아리] 2학기 신입 기수 모집!', date: '10.24' },
          { text: '코딩 동아리에서 해커톤 팀원 구합니다', date: '10.23' },
          { text: '사진동아리 정기 전시회 개최 안내', date: '10.22' },
          { text: '영화 감상 동아리 주말 상영작 안내', date: '10.20' },
          { text: '댄스동아리 버스킹 공연 (학생회관 앞)', date: '10.18' },
        ]} />
      </div>
    </>
  )
}

function BoardCard({ title, items }) {
  return (
    <div style={boardCardStyle}>
      <h2 style={boardTitleStyle}>{title}</h2>
      <ul style={{ listStyle: 'none' }}>
        {items.map((item, i) => (
          <li key={i} style={boardItemStyle}>
            <span>{item.text}</span>
            <span style={{ color: '#64748b', fontSize: '0.82rem' }}>{item.date}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

// ── 인라인 스타일 ──────────────────────────────────────────────────────────
const heroStyle = {
  position: 'relative', width: '100%', height: '100vh',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
}
const canvasStyle = {
  position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 0,
}

const uiStyle = {
  position: 'absolute',   // relative → absolute
  top: '10vh',            // 화면 상단에서 15% 위치 (숫자 낮출수록 더 위로 올라감)
  left: '50%',
  transform: 'translateX(-50%)',
  zIndex: 10, textAlign: 'center',
  pointerEvents: 'none',
}

const titleStyle = {

  fontSize: 'clamp(2.5rem, 6vw, 5rem)',
  fontWeight: 700, letterSpacing: '0.05em',
  background: 'linear-gradient(135deg, #00d4ff, #a855f7)',
  WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
  marginBottom: '1rem',
}
const subtitleStyle = {
  color: '#64748b', fontSize: '1rem', letterSpacing: '0.1em',
}
const boardSectionStyle = {
  display: 'flex', gap: '2rem', flexWrap: 'wrap', justifyContent: 'center',
  padding: '80px 40px', maxWidth: '1200px', margin: '0 auto',
}
const boardCardStyle = {
  flex: '1 1 380px', background: 'rgba(255,255,255,0.04)',
  border: '1px solid rgba(0,212,255,0.15)', borderRadius: '16px',
  padding: '32px', backdropFilter: 'blur(10px)',
}
const boardTitleStyle = {
  fontSize: '1.1rem', fontWeight: 600, color: '#00d4ff',
  marginBottom: '20px', letterSpacing: '0.05em',
}
const boardItemStyle = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  padding: '12px 0', borderBottom: '1px solid rgba(255,255,255,0.06)',
  fontSize: '0.88rem', color: '#cbd5e1', gap: '12px',
}