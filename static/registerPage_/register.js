// 커스텀 커서
const cursorDot = document.querySelector('.cursor-dot');
const cursorOutline = document.querySelector('.cursor-outline');

window.addEventListener('mousemove', (e) => {
    cursorDot.style.left = `${e.clientX}px`;
    cursorDot.style.top = `${e.clientY}px`;

    cursorOutline.animate({
        left: `${e.clientX}px`,
        top: `${e.clientY}px`
    }, { duration: 500, fill: "forwards" });
});

/* 인풋 위에서 커서 점을 흐리게 */
document.querySelectorAll('input').forEach(el => {
    el.addEventListener('mouseenter', () => { cursorDot.style.opacity = '0.4'; });
    el.addEventListener('mouseleave', () => { cursorDot.style.opacity = '1'; });
});

// Three.js 파티클 배경
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x050505, 0.04);

const container = document.getElementById('canvas-container');
const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
camera.position.z = 18;
camera.position.y = 2;

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(window.devicePixelRatio);
container.appendChild(renderer.domElement);

/* 파란 파티클 */
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 1200;
const posArray = new Float32Array(particlesCount * 3);
for (let i = 0; i < particlesCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 60;
}
particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
const particlesMaterial = new THREE.PointsMaterial({
    size: 0.07, color: 0x00d4ff,
    transparent: true, opacity: 0.75,
    blending: THREE.AdditiveBlending
});
const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

/* 분홍 보조 파티클 */
const posArray2 = new Float32Array(600 * 3);
for (let i = 0; i < 600 * 3; i++) posArray2[i] = (Math.random() - 0.5) * 70;
const geo2 = new THREE.BufferGeometry();
geo2.setAttribute('position', new THREE.BufferAttribute(posArray2, 3));
const mat2 = new THREE.PointsMaterial({
    size: 0.05, color: 0xff00c8,
    transparent: true, opacity: 0.5,
    blending: THREE.AdditiveBlending
});
scene.add(new THREE.Points(geo2, mat2));

/* 홀로그램 링 오브젝트 */
const ringGroup = new THREE.Group();
scene.add(ringGroup);
for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * Math.PI * 2;
    const geo = new THREE.TorusGeometry(1.2 + Math.random() * 0.5, 0.02, 8, 60);
    const mat = new THREE.MeshBasicMaterial({
        color: new THREE.Color().setHSL(i / 8, 1, 0.5),
        transparent: true, opacity: 0.3,
        blending: THREE.AdditiveBlending
    });
    const ring = new THREE.Mesh(geo, mat);
    ring.position.x = Math.cos(angle) * 12;
    ring.position.z = Math.sin(angle) * 12;
    ring.position.y = Math.sin(angle * 2) * 2;
    ring.rotation.x = Math.PI / 2;
    ringGroup.add(ring);
}

/* 애니메이션 루프 */
const clock = new THREE.Clock();
function animate() {
    requestAnimationFrame(animate);
    const t = clock.getElapsedTime();
    particlesMesh.rotation.y = t * 0.04;
    particlesMesh.position.y = Math.sin(t * 0.4) * 1.5;
    ringGroup.rotation.y = t * 0.06;
    ringGroup.children.forEach((ring, idx) => {
        ring.position.y = Math.sin(t * 1.2 + idx) * 1.5;
        ring.rotation.z = t * 0.3 + idx;
    });
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});

// 회원가입
function register() {
    let form = document.getElementById('registerForm');
    let formData = new FormData(form);

    fetch('/auth/register', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                window.location.href = '/auth/login'; // 성공하면 로그인 화면으로 이동
            }
        });
}