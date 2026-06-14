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

/* 인풋 위에서는 커서를 원래대로 보여주기 */
document.querySelectorAll('input').forEach(el => {
    el.addEventListener('mouseenter', () => {
        cursorDot.style.opacity = '0.4';
    });
    el.addEventListener('mouseleave', () => {
        cursorDot.style.opacity = '1';
    });
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

/* 파티클(별가루) 배경 */
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 1200;
const posArray = new Float32Array(particlesCount * 3);
for (let i = 0; i < particlesCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 60;
}
particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

const particlesMaterial = new THREE.PointsMaterial({
    size: 0.07,
    color: 0x00d4ff,
    transparent: true,
    opacity: 0.75,
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

/* 홀로그램 링 */
const ringGroup = new THREE.Group();
scene.add(ringGroup);

for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * Math.PI * 2;
    const geo = new THREE.TorusGeometry(1.2 + Math.random() * 0.5, 0.02, 8, 60);
    const mat = new THREE.MeshBasicMaterial({
        color: new THREE.Color().setHSL(i / 8, 1, 0.5),
        transparent: true,
        opacity: 0.3,
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

// 로그인
function login() {
    const errorMsg = document.getElementById('errorMsg');
    errorMsg.classList.remove('show');

    let form = document.getElementById('loginForm');
    let formData = new FormData(form);

    fetch('/auth/login', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url || '/';
            } else {
                errorMsg.textContent = data.message || '아이디 또는 비밀번호를 확인해주세요.';
                errorMsg.classList.add('show');
            }
        })
        .catch(() => {
            errorMsg.textContent = '서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.';
            errorMsg.classList.add('show');
        });
}

/* 엔터 키로 로그인 */
document.getElementById('password').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') login();
});
document.getElementById('user_id').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('password').focus();
});